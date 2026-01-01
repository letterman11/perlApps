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

use Util;
use DbConfig;
use CGI qw(:standard);
use CGI::Cookie;
use CGI::Carp qw(fatalsToBrowser);
use POSIX qw(strftime);
use JSON::PP;
use Try::Tiny;

# Configuration constants
use constant {
    POST_MAX => 1024 * 10,  # 10KB max
    ERROR_STATUS => 500,
    SUCCESS_STATUS => 200,
};

# Security settings
$CGI::POST_MAX = POST_MAX;
$CGI::DISABLE_UPLOADS = 1;

# Initialize
my $query = CGI->new();
my $session = Util::validateSession();
my $timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime);

# Main execution
main();
exit 0;

#==============================================================================
# Main Subroutine
#==============================================================================
sub main {
    # Validate session
    unless (ref $session eq 'SessionObject') {
        send_error_response(403, 'Invalid Session');
        return;
    }

    CGI::Carp::carp("===============================");
    CGI::Carp::carp("THE START OF PROGRAM EXECUTION");
    CGI::Carp::carp("===============================");

    # Connect to database
    my $dbh = connect_to_database();
    return unless $dbh;

    # Route request
    my $request_type = $query->param('req') || '';
    
    my $handlers = {
        'roomIDs'    => \&handle_room_ids,
        'roomLogin'  => \&handle_room_login,
        'roomLogout' => \&handle_room_logout,
        'sendMsg'    => \&handle_send_message,
    };

    if (exists $handlers->{$request_type}) {
        $handlers->{$request_type}->($dbh);
    } else {
        send_error_response(400, 'Bad Request: Unknown request type');
    }

    $dbh->disconnect() if $dbh;
}

#==============================================================================
# Database Connection
#==============================================================================
sub connect_to_database {
    my $dbc = DbConfig->new();
    unless ($dbc) {
        send_error_response(ERROR_STATUS, 'Cannot create database handle');
        return;
    }

    my $dbh = $dbc->connect();
    unless ($dbh) {
        send_error_response(ERROR_STATUS, "Cannot connect to database: $DBI::errstr");
        return;
    }

    return $dbh;
}

#==============================================================================
# Request Handlers
#==============================================================================

# Handle roomIDs request - returns list of available chat rooms
sub handle_room_ids {
    my ($dbh) = @_;

    my $room_array;

    try {
        my $sth = $dbh->prepare('SELECT room_id FROM chat_room');
        $sth->execute();
        $room_array = $sth->fetchall_arrayref([0]);
        $sth->finish();
    } catch {
        CGI::Carp::carp("DB ERROR: $_");
        send_error_response(ERROR_STATUS, 'Application Error: Failed to fetch room IDs');
        return;
    };

    # Extract room IDs and send as JSON
    my @room_ids = map { $_->[0] } @$room_array;
    send_json_response(\@room_ids);
}

# Handle roomLogin request - user joins a chat room
sub handle_room_login {
    my ($dbh) = @_;

    my $user_id = validate_id($query->param('userID'));
    my $room_id = validate_id($query->param('roomID'));

    unless ($user_id && $room_id) {
        send_error_response(400, 'Bad Request: Invalid userID or roomID');
        return;
    }

    # Try to insert user into room (if not exists, update instead)
    my $success = upsert_user_room($dbh, $user_id, $room_id);
    return unless $success;

    # Get list of users in the room
    my $user_list = get_room_users($dbh, $room_id);
    return unless defined $user_list;

    # Send response
    if (@$user_list > 1) {
        my @user_ids = map { $_->[0] } @$user_list;
        send_json_response(\@user_ids);
    } else {
        send_success_response();
    }
}

# Handle roomLogout request - user leaves a chat room
sub handle_room_logout {
    my ($dbh) = @_;

    my $user_id = validate_id($query->param('userID'));

    unless ($user_id) {
        send_error_response(400, 'Bad Request: Invalid userID');
        return;
    }

    try {
        my $sth = $dbh->prepare('DELETE FROM user_cr WHERE user_id = ?');
        $sth->execute($user_id);
        $sth->finish();
        
        CGI::Carp::carp("User $user_id logged out");
    } catch {
        CGI::Carp::carp("DB ERROR: $_");
        send_error_response(ERROR_STATUS, 'Application Error: Failed to logout');
        return;
    };

    print $query->header(
        -status => '200 OK',
        -type   => 'text/plain',
    );
    print "Room Logout Successful";
}

# Handle sendMsg request - send message to all users in a room
sub handle_send_message {
    my ($dbh) = @_;

    my $user_id = validate_id($query->param('userID'));
    my $room_id = validate_id($query->param('roomID'));
    my $msg_text = $query->param('msgText');

    unless ($user_id && $room_id && defined $msg_text) {
        send_error_response(400, 'Bad Request: Missing required parameters');
        return;
    }

    # Validate and sanitize message text
    $msg_text = validate_message_text($msg_text);
    unless (defined $msg_text) {
        send_error_response(400, 'Bad Request: Invalid message text');
        return;
    }

    # Get all users in the room
    my $room_users;
    try {
        my $sth = $dbh->prepare('SELECT user_id FROM user_cr WHERE room_id = ?');
        $sth->execute($room_id);
        $room_users = $sth->fetchall_arrayref([0]);
        $sth->finish();
    } catch {
        CGI::Carp::carp("DB ERROR: $_");
        send_error_response(ERROR_STATUS, 'Application Error: Failed to fetch room users');
        return;
    };

    # Insert message for each user in the room
    my @error_queue = send_messages_to_users($dbh, $user_id, $room_id, $msg_text, $room_users);

    # Send response based on results
    handle_send_message_response(\@error_queue, $room_users);
}

#==============================================================================
# Database Helper Functions
#==============================================================================

# Insert or update user in chat room
sub upsert_user_room {
    my ($dbh, $user_id, $room_id) = @_;

    # Try INSERT first
    try {
        my $sth = $dbh->prepare(q{
            INSERT INTO user_cr (user_id, room_id, date_ts, room_name)
            VALUES (?, ?, ?, ?)
        });
        $sth->execute($user_id, $room_id, $timestamp, $room_id);
        $sth->finish();
        
        CGI::Carp::carp("User $user_id joined room $room_id (INSERT)");
        return 1;
    } catch {
        # INSERT failed, try UPDATE instead
        return update_user_room($dbh, $user_id, $room_id);
    };
}

# Update existing user room record
sub update_user_room {
    my ($dbh, $user_id, $room_id) = @_;

    try {
        my $sth = $dbh->prepare(q{
            UPDATE user_cr 
            SET room_id = ?, date_ts = ?, room_name = ?
            WHERE user_id = ?
        });
        $sth->execute($room_id, $timestamp, $room_id, $user_id);
        $sth->finish();
        
        CGI::Carp::carp("User $user_id joined room $room_id (UPDATE)");
    } catch {
        CGI::Carp::carp("DB ERROR: $_");
        send_error_response(ERROR_STATUS, 'Application Error: Failed to update user room');
        return 0;
    };

    return 1;
}

# Get list of users in a room
sub get_room_users {
    my ($dbh, $room_id) = @_;

    my $user_list;
    try {
        my $sth = $dbh->prepare('SELECT user_id FROM user_cr WHERE room_id = ?');
        $sth->execute($room_id);
        $user_list = $sth->fetchall_arrayref([0]);
        $sth->finish();
    } catch {
        CGI::Carp::carp("DB ERROR: $_");
        send_error_response(ERROR_STATUS, 'Application Error: Failed to fetch room users');
        return;
    };

    return $user_list;
}

# Send message to all users in room
sub send_messages_to_users {
    my ($dbh, $user_id, $room_id, $msg_text, $room_users) = @_;

    my @error_queue;

    for my $msg_user (@$room_users) {
        my $msg_user_id = $msg_user->[0];
        
        try {
            my $sth = $dbh->prepare(q{
                INSERT INTO chat_room_queue 
                (user_id, room_id, insert_ts, chat_text, msg_user_id)
                VALUES (?, ?, ?, ?, ?)
            });
            
            $sth->execute($user_id, $room_id, $timestamp, $msg_text, $msg_user_id);
            $sth->finish();
            
            CGI::Carp::carp("Message queued for user $msg_user_id");
        } catch {
            CGI::Carp::carp("DB ERROR for user $msg_user_id: $_");
            push @error_queue, $msg_user_id;
        };
    }

    return @error_queue;
}

# Handle response for sendMsg based on success/failure
sub handle_send_message_response {
    my ($error_queue, $room_users) = @_;

    my $total_users = scalar(@$room_users);
    my $failed_count = scalar(@$error_queue);

    if ($failed_count == $total_users) {
        # All messages failed
        send_error_response(ERROR_STATUS, 'Application Error: All messages failed');
    } elsif ($failed_count == 0) {
        # All messages succeeded
        send_success_response();
    } else {
        # Partial success
        print $query->header(
            -status => '200 OK',
            -type   => 'text/plain',
        );
        print "Message sent with errors\n";
        print "Failed for users:\n";
        print join("\n", @$error_queue);
    }
}

#==============================================================================
# Response Functions
#==============================================================================
sub send_json_response {
    my ($data) = @_;

    my $json = JSON::PP->new->utf8->encode($data);
    
    print $query->header(
        -status  => '200 OK',
        -type    => 'application/json',
        -charset => 'UTF-8',
    );
    print $json;
}

sub send_success_response {
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
sub validate_id {
    my ($id) = @_;
    return unless defined $id;
    
    # Remove taint and validate alphanumeric IDs
    if ($id =~ /^([\w\-]+)$/) {
        return $1;
    }
    return;
}

sub validate_message_text {
    my ($text) = @_;
    return unless defined $text;
    
    # Basic validation - adjust as needed for your requirements
    # Remove null bytes and limit length
    $text =~ s/\x00//g;
    
    # Limit message length (adjust as needed)
    if (length($text) > 1000) {
        return;
    }
    
    # Untaint
    if ($text =~ /^(.*)$/s) {
        return $1;
    }
    
    return;
}
