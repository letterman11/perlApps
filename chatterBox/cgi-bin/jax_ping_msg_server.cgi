#!/usr/bin/perl -wT
use strict;
use warnings;
use utf8;

use FindBin qw($Bin);
our $untainted_bin;

BEGIN {
    # Extract the trusted part of $Bin using a regular expression
    # This assumes $Bin contains a valid path and removes any potentially malicious characters.
    ($untainted_bin) = $Bin =~ /^(.+)$/;
}

use lib "$untainted_bin/../../../private/chatterBox/script_src";

# Enable taint mode for security
use English qw(-no_match_vars);
$ENV{PATH} = '/bin:/usr/bin';
delete @ENV{qw(IFS CDPATH ENV BASH_ENV)};

use DbGlob;
use Util;
use CGI qw(:standard);
use CGI::Cookie;
use CGI::Carp qw(fatalsToBrowser);
use JSON::PP;
use Try::Tiny;

# Configuration constants
use constant {
    POST_MAX => 1024 * 10,  # 10KB max
    DB_ERROR_PREFIX => 'ping server - DB ERROR',
};

# Security settings
$CGI::POST_MAX = POST_MAX;
$CGI::DISABLE_UPLOADS = 1;

# Initialize
my $query = CGI->new();
my $session = Util::validateSession();

# Main execution
main();
exit 0;

#==============================================================================
# Main Subroutine
#==============================================================================
sub main {
    # Validate session
    unless (ref $session eq 'SessionObject') {
        send_error_response(401, 'Unauthorized: Invalid session');
        return;
    }

    # Connect to database
    my $dbh = connect_to_database();
    return unless $dbh;

    # Route request
    my $request_type = $query->param('req') || '';
    
    if ($request_type eq 'ajaxPing') {
        handle_ajax_ping($dbh);
    } else {
        send_error_response(400, 'Bad Request: Unknown request type');
    }

    $dbh->disconnect() if $dbh;
}

#==============================================================================
# Database Connection
#==============================================================================
sub connect_to_database {
    my $dbg = DbGlob->new();
    unless ($dbg) {
        send_error_response(500, 'Cannot create database handle');
        return;
    }

    my $dbh = $dbg->connect();
    unless ($dbh) {
        send_error_response(500, "Cannot connect to database: $DBI::errstr");
        return;
    }

    return $dbh;
}

#==============================================================================
# Ajax Ping Handler
#==============================================================================
sub handle_ajax_ping {
    my ($dbh) = @_;

    # Get and validate parameters
    my $user_id = validate_user_id($query->param('userID'));
    my $room_id = validate_room_id($query->param('roomID'));

    unless ($user_id && $room_id) {
        send_error_response(400, 'Bad Request: Invalid userID or roomID');
        return;
    }

    # Fetch user and room data
    my ($user_cr_row, $msg_user_array) = fetch_user_room_data($dbh, $user_id, $room_id);
    return unless defined $user_cr_row;

    # Fetch message queue
    my $msg_queue_array = fetch_message_queue($dbh, $user_id, $user_cr_row->{date_ts});
    return unless defined $msg_queue_array;

    # Process messages if any exist
    if (@$msg_queue_array > 0) {
        process_messages($dbh, $msg_queue_array, $msg_user_array);
    } elsif (@$msg_user_array > 1) {
        send_user_list_response($msg_user_array);
    } else {
        send_empty_response();
    }
}

#==============================================================================
# Data Fetching Functions
#==============================================================================
sub fetch_user_room_data {
    my ($dbh, $user_id, $room_id) = @_;

    my ($user_cr_row, $msg_user_array);

    try {
        # Fetch user's chat room record using prepared statement
        my $sth1 = $dbh->prepare(
            'SELECT user_id, room_id, date_ts FROM user_cr WHERE user_id = ?'
        );
        $sth1->execute($user_id);
        my @row = $sth1->fetchrow_array();
        $sth1->finish();

        if (@row) {
            $user_cr_row = {
                user_id => $row[0],
                room_id => $row[1],
                date_ts => $row[2],
            };
        }

        # Fetch users in the same room
        my $sth2 = $dbh->prepare(
            'SELECT user_id FROM user_cr WHERE room_id = ?'
        );
        $sth2->execute($room_id);
        $msg_user_array = $sth2->fetchall_arrayref([0]);
        $sth2->finish();

    } catch {
        CGI::Carp::carp(DB_ERROR_PREFIX . " $_");
        send_error_response(500, 'Application Error: Failed on user_cr select');
        return;
    };

    return ($user_cr_row, $msg_user_array);
}

sub fetch_message_queue {
    my ($dbh, $user_id, $date_ts) = @_;

    my $msg_queue_array;

    try {
        my $sth = $dbh->prepare(q{
            SELECT cr_queue_id, user_id, room_id, insert_ts, chat_text, msg_user_id
            FROM chat_room_queue
            WHERE msg_user_id = ?
              AND insert_ts >= ?
            ORDER BY cr_queue_id DESC
            LIMIT 2
        });
        
        $sth->execute($user_id, $date_ts);
        $msg_queue_array = $sth->fetchall_arrayref({});
        $sth->finish();

    } catch {
        CGI::Carp::carp(DB_ERROR_PREFIX . " $_");
        send_error_response(500, 'Application Error: Failed ChatRoom Select');
        return;
    };

    return $msg_queue_array;
}

#==============================================================================
# Message Processing
#==============================================================================
sub process_messages {
    my ($dbh, $msg_queue_array, $msg_user_array) = @_;

    # Delete processed messages
    my $deleted = delete_message_queue($dbh, $msg_queue_array);
    return unless $deleted;

    # Build and send JSON response
    send_message_response($msg_queue_array, $msg_user_array);
}

sub delete_message_queue {
    my ($dbh, $msg_queue_array) = @_;

    my @queue_ids = map { $_->{cr_queue_id} } @$msg_queue_array;
    my $placeholders = join(',', ('?') x @queue_ids);

    try {
        my $sth = $dbh->prepare(
            "DELETE FROM chat_room_queue WHERE cr_queue_id IN ($placeholders)"
        );
        $sth->execute(@queue_ids);
        $sth->finish();

        CGI::Carp::carp("Deleted queue IDs: " . join(', ', @queue_ids));

    } catch {
        CGI::Carp::carp(DB_ERROR_PREFIX . " $_");
        send_error_response(500, 'Application Error: Failed ChatRoom Delete');
        return 0;
    };

    return 1;
}

#==============================================================================
# Response Functions
#==============================================================================
sub send_message_response {
    my ($msg_queue_array, $msg_user_array) = @_;

    # Build messages array
    my @messages = map {
        {
            user_id    => $_->{user_id},
            room_id    => $_->{room_id},
            msg_text   => $_->{chat_text},
            msg_q_id   => $_->{cr_queue_id},
            time_stamp => $_->{insert_ts},
        }
    } @$msg_queue_array;

    # Build response hash
    my $response = { messages => \@messages };

    # Add user list if multiple users
    if (@$msg_user_array > 1) {
        my @user_ids = map { $_->[0] } @$msg_user_array;
        $response->{msg_user_ids} = \@user_ids;
    }

    send_json_response($response);
}

sub send_user_list_response {
    my ($msg_user_array) = @_;

    my @user_ids = map { $_->[0] } @$msg_user_array;
    my $response = { msg_user_ids => \@user_ids };

    send_json_response($response);
}

sub send_json_response {
    my ($data) = @_;

    my $json = JSON::PP->new->utf8->pretty->encode($data);
    
    CGI::Carp::carp("JSON response: $json");
    CGI::Carp::carp("Process ID: $$");

    print $query->header(
        -status       => '200 OK',
        -type         => 'application/json',
        -charset      => 'UTF-8',
    );
    print $json;
}

sub send_empty_response {
    print $query->header(-status => '200 OK');
}

sub send_error_response {
    my ($code, $message) = @_;
    
    print $query->header(
        -status => "$code $message",
        -type   => 'text/plain',
    );
}

#==============================================================================
# Input Validation
#==============================================================================
sub validate_user_id {
    my ($user_id) = @_;
    return unless defined $user_id;
    
    # Remove taint and validate (adjust pattern as needed)
    if ($user_id =~ /^(\w+)$/) {
        return $1;
    }
    return;
}

sub validate_room_id {
    my ($room_id) = @_;
    return unless defined $room_id;
    
    # Remove taint and validate (adjust pattern as needed)
    if ($room_id =~ /^(\w+)$/) {
        return $1;
    }
    return;
}
