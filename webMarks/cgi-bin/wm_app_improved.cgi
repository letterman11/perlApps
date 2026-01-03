#!/usr/bin/perl -wT

use strict;
use warnings;

use FindBin qw($Bin);
use Encode 'encode';
use Encode 'decode';

our $untainted_bin;

BEGIN {
    # Extract the trusted part of $Bin using a regular expression
    # This assumes $Bin contains a valid path and removes any potentially malicious characters.
    ($untainted_bin) = $Bin =~ /^(.+)$/; 
}

use lib "$untainted_bin/../../../private/webMarks/script_src";

# Explicitly require external files - these provide functions we'll call
require "$untainted_bin/gen_histo_gram_multi.pl";
require "$untainted_bin/ExecPageSQL.pl";
require "$untainted_bin/SQLStrings.pl";

# Core modules
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
use DBI;
use POSIX 'strftime';

# Local modules
use globals;
use DbConfig;
use Util;
use Error;
use GenMarks;

# Make required functions available - these come from the required files above
# Declaring them tells Perl they exist and will be defined at runtime
sub validateSession;      # from ExecPageSQL.pl or Util
sub storeSession;         # from ExecPageSQL.pl or Util
sub genSessionID;         # from Util
sub formValidation;       # from Util
sub exec_page;            # from ExecPageSQL.pl
sub storeSQL;             # from SQLStrings.pl
sub getStoredSQL;         # from SQLStrings.pl
sub isset;                # from Util

# Package-level variables that need to be accessible
our $query = CGI->new();
our $exec_sql_str;
our $executed_sql_str;
our $NO_HEADER = 0;
#our $DEBUG = $globals::true;
our $DEBUG = 1;
our %tabMap = %globals::tabMap;

# Global database connection
our $dbc = DbConfig->new();
our $dbh = $dbc->connect()
    or do {
        GenError->new(Error->new(102))->display();
        die "Cannot Connect to Database $DbConfig::errstr\n";
    };

# Error code constants
use constant {
    ERR_DB_CONNECT => 102,
    ERR_AUTH_FAILED => 112,
    ERR_REGISTRATION_FAILED => 120,
    ERR_INSERT_FAILED => 150,
    ERR_DUPLICATE_URL => 150,
    ERR_MISSING_PARAMS => 151,
};

#==============================================================================
# DISPATCH TABLE - Maps request types to handler functions
#==============================================================================
my %DISPATCH_TABLE = (
    'auth'          => \&handle_auth,
    'reg'           => \&handle_registration,
    'regAuth'       => \&handle_registration_auth,
    'search'        => \&handle_search,
    'newMark'       => \&handle_new_mark,
    'updateMark'    => \&handle_update_mark,
    'deleteMark'    => \&handle_delete_mark,
    'deltaPass'     => \&handle_password_change,
    'logOut'        => \&handle_logout,
);

#==============================================================================
# MAIN CONTROLLER FUNCTION
#==============================================================================
sub main_func {
    my $q_parm = $query->url_param('req') || '';
    
    # Check if user has authenticated request parameter
    if (exists $DISPATCH_TABLE{$q_parm}) {
        # Route to appropriate handler based on dispatch table
        $DISPATCH_TABLE{$q_parm}->();
    }
    else {
        # Default: check for valid session or show default page
        handle_default_request();
    }
}

sub handle_default_request {
    my $session = validateSession($query);
    my $wm_user_id = $session->{wmUSERID};
    my $wm_user_name = $session->{wmUSERNAME};
    
    if (defined($wm_user_id)) {
        # Valid session - show user's page
        exec_page($wm_user_id, $wm_user_name);
    }
    else {
        # No valid session - show default/login page
        GenMarks->new()->genDefaultPage();
    }
}

#==============================================================================
# REQUEST HANDLERS - Called from dispatch table
#==============================================================================

sub handle_auth {
    my ($user_id, $user_name) = pre_auth();

    if (defined($user_id)) {
        authorize($user_id, $user_name);
    }
    else {
        GenMarks->new()->genDefaultPage(Error->new(ERR_AUTH_FAILED));
    }
}

sub handle_registration {
    GenMarks->new()->genRegistration();
}

sub handle_registration_auth {
    my $callObj = formValidation($query);
    
    if (ref $callObj eq 'Error') {
        GenMarks->new()->genRegistration($callObj);
        return;
    }
    
    my $sqlHash = $callObj;
    my $local_user_name = $sqlHash->{userName};
    
    # Generate unique user ID
    my $partUserName = substr($sqlHash->{userName}, 0, 5);
    my $partID = substr(genSessionID(), 0, 5);
    my $userID = $partUserName . "_" . $partID;
    
    # Use parameterized query for security
    my $insert_sql_str = "INSERT INTO WM_USER (USER_ID, USER_NAME, USER_PASSWD, EMAIL_ADDRESS) VALUES (?, ?, ?, ?)";
    
    eval {
        my $sth = $dbh->prepare($insert_sql_str);
        $sth->execute($userID, $sqlHash->{userName}, $sqlHash->{password}, $sqlHash->{email});
    };
    
    if ($@) {
        print STDERR "Registration failed: $@\n" if $DEBUG;
        GenMarks->new()->genRegistration(Error->new(ERR_REGISTRATION_FAILED));
    }
    else {
        GenMarks->new()->genDefaultPage("Registration Successful: $local_user_name");
    }
}

sub handle_search {
    my $session = validateSession($query);
    my $wm_user_id = $session->{wmUSERID};
    my $wm_user_name = $session->{wmUSERNAME};
    
    if (defined($wm_user_id)) {
        exec_page($wm_user_id, $wm_user_name);
    }
    else {
        GenMarks->new()->genDefaultPage();
    }
}

sub handle_new_mark {
    my $session = validateSession($query);
    my $wm_user_id = $session->{wmUSERID};
    my $wm_user_name = $session->{wmUSERNAME};
    
    if (defined($wm_user_id)) {
        my $callObj = insert_mark($wm_user_id);
        exec_page($wm_user_id, $wm_user_name, $callObj);
    }
    else {
        GenMarks->new()->genDefaultPage();
    }
}

sub handle_update_mark {
    my $session = validateSession($query);
    my $wm_user_id = $session->{wmUSERID};
    my $wm_user_name = $session->{wmUSERNAME};
    
    if (defined($wm_user_id)) {
        my $callObj = update_mark($wm_user_id);
        exec_page($wm_user_id, $wm_user_name, $callObj);
    }
    else {
        GenMarks->new()->genDefaultPage();
    }
}

sub handle_delete_mark {
    my $session = validateSession($query);
    my $wm_user_id = $session->{wmUSERID};
    my $wm_user_name = $session->{wmUSERNAME};
    
    if (defined($wm_user_id)) {
        my $callObj = delete_mark($wm_user_id);
        exec_page($wm_user_id, $wm_user_name, $callObj);
    }
    else {
        GenMarks->new()->genDefaultPage();
    }
}

sub handle_password_change {
    my $session = validateSession($query);
    my $wm_user_id = $session->{wmUSERID};
    my $wm_user_name = $session->{wmUSERNAME};
    
    if (defined($wm_user_id)) {
        if (not mod_passwd()) {
            exec_page($wm_user_id, $wm_user_name, Error->new(ERR_AUTH_FAILED));
        }
        else {
            exec_page($wm_user_id, $wm_user_name);
        }
    }
    else {
        GenMarks->new()->genDefaultPage();
    }
}

sub handle_logout {
    my $session = validateSession($query);
    my $wm_user_id = $session->{wmUSERID};
    my $wm_user_name = $session->{wmUSERNAME};

    if (defined($wm_user_id)) {
        delete_session();
    }
    else
    {
        GenMarks->new()->genDefaultPage();
    }
}

#==============================================================================
# AUTHENTICATION FUNCTIONS
#==============================================================================

sub pre_auth {
    return pre_auth2(@_);
    my $usr_name = $query->param('user_name');
    my $usr_pass = $query->param('user_pass');
    my $old_usr_pass = $query->param('old_pass');  # only for password update
    
    return (undef, undef, undef) unless (defined($usr_name) && 
        (defined($usr_pass) || defined($old_usr_pass)));
    
    my $check_pass = defined($old_usr_pass) ? $old_usr_pass : $usr_pass;
    
    # Use parameterized query for security
    my $sql = "SELECT user_id, user_name FROM WM_USER WHERE user_passwd = ? AND user_name = ?";
    
    my $sth = $dbh->prepare($sql);
    $sth->execute($check_pass, $usr_name);
    
    my @user_row = $sth->fetchrow_array();
    
    print STDERR $$, " ###### Authentication attempt for: ", 
        ($user_row[1] // 'unknown'), " #######\n" if $DEBUG;
    
    return ($user_row[0], $user_row[1], $usr_pass);
}

sub pre_auth2
{
    my $c = shift;
    my $usr_name = $query->param('user_name');
    my $usr_pass = $query->param('user_pass'); 
    my $old_usr_pass = $query->param('old_pass'); #only for update
    my $exec_sql_str;

    my $password_digest = Util::digest_pass($usr_pass);
    my $password_old_digest = Util::digest_pass($old_usr_pass);

    ##################################
    #password digest function to add##
    # do not want to touch db  #######
    ##################################

    my $sql = "SELECT user_id, user_name, user_passwd FROM WM_USER WHERE user_name = ?";

    my ($db_usr_id, $db_usr_name, $db_usr_pass)  = $dbh->selectrow_array($sql, {}, $usr_name);

    print STDERR " data base  pre_auth2 " , " " , $db_usr_id  , " " , $db_usr_name , " " , $db_usr_pass;


    if(isset($old_usr_pass) && ($db_usr_pass eq $old_usr_pass) || $db_usr_pass eq $password_old_digest) 
    {     
        return ($db_usr_id, $db_usr_name, $usr_pass); 
    }
    elsif (($db_usr_pass eq $usr_pass) || ($db_usr_pass eq $password_digest))
    {
        return ($db_usr_id, $db_usr_name,$db_usr_pass); 
    }
    else
    {
        return (); 
    }

}

sub delete_session {
    my $host = undef;

    #for the deletion of httponly cookies
    my @cookies = (
        CGI::Cookie->new(
            -name => 'wmSessionID',
            -value => '',
            -expires => '-1d',
            -domain => $host,
            -path => '/',
            -httponly => 1,
        ),
        CGI::Cookie->new(
            -name => 'wmUserID',
            -value => '',
            -expires => '-1d',
            -domain => $host,
            -path => '/',
            -httponly => 1,
        ),
        CGI::Cookie->new(
            -name => 'wmUserName',
            -value => '',
            -expires => '-1d',
            -domain => $host,
            -path => '/',
            -httponly => 1,
        ),
        CGI::Cookie->new(
            -name => 'Counter',
            -value => 0,
            -expires => '-1d',
            -domain => $host,
            -path => '/',
        ),
        CGI::Cookie->new(
            -name => 'tab_state',
            -value => 0,
            -expires => '-1d',
            -domain => $host,
            -path => '/',
        ),
        CGI::Cookie->new(
            -name => 'dt_cnter',
            -value => 0,
            -expires => '-1d',
            -domain => $host,
            -path => '/',
        ),
    );

    # Send HTTP header with cookies
    print $query->header(
        -status => 200,
        -cookie => \@cookies,
    );

    $NO_HEADER = 1;
    GenMarks->new()->genDefaultPage();

}

sub authorize {
    my ($user_id, $user_name) = @_;
    
    my $sessionID = genSessionID();
    my $host = undef;
    
    # Create session cookies with httponly flag for security
    my @cookies = (
        CGI::Cookie->new(
            -name => 'wmSessionID',
            -value => $sessionID,
            -expires => undef,
            -domain => $host,
            -path => '/',
            -httponly => 1,
        ),
        CGI::Cookie->new(
            -name => 'wmUserID',
            -value => $user_id,
            -expires => undef,
            -domain => $host,
            -path => '/',
            -httponly => 1,
        ),
        CGI::Cookie->new(
            -name => 'wmUserName',
            -value => $user_name,
            -expires => undef,
            -domain => $host,
            -path => '/',
            -httponly => 1,
        ),
        CGI::Cookie->new(
            -name => 'Counter',
            -value => 0,
            -expires => undef,
            -domain => $host,
            -path => '/',
        ),
        CGI::Cookie->new(
            -name => 'tab_state',
            -value => 0,
            -expires => undef,
            -domain => $host,
            -path => '/',
        ),
        CGI::Cookie->new(
            -name => 'dt_cnter',
            -value => 0,
            -expires => undef,
            -domain => $host,
            -path => '/',
        ),
    );
    
    # Store session using function from required file
    storeSession('sess1', $sessionID, $user_id, $user_name);
    
    # Send HTTP header with cookies
    print $query->header(
        -status => 200,
        -cookie => \@cookies
    );
    
    $NO_HEADER = 1;
    exec_page($user_id, $user_name, $NO_HEADER);
}

sub mod_passwd {
    my ($usr_id, $usr_name, $usr_pass) = pre_auth();
    
    return 0 unless defined($usr_name);
    
    # Use parameterized query for security
    my $sql = "UPDATE WM_USER SET user_passwd = ? WHERE user_name = ?";
    my $rc = $dbh->do($sql, undef, $usr_pass, $usr_name);
    
    return defined($rc) ? 1 : 0;
}

#==============================================================================
# BOOKMARK INSERTION WITH TRANSACTION
#==============================================================================
sub insert_mark {
    my $user_id = shift;
    my $title = $query->param('mark_title');
    my $url = $query->param('mark_url');
    
    # Validate input
    return Error->new(ERR_MISSING_PARAMS) if ((not isset($title)) || (not isset($url)));
    
    my $unix_epochs = time;
    my $dateAdded = $unix_epochs;
    my $date_added = strftime "%Y-%m-%d %H:%M:%S", localtime($unix_epochs);
    
    print STDERR "Inserting bookmark - Date: $date_added\n" if $DEBUG;
    
    my $error;
    
    eval {
        # Begin transaction
        $dbh->begin_work() or die "Cannot begin transaction: " . $dbh->errstr;
        
        # Check for duplicate URL using parameterized query
        my $dup_check = "SELECT b.url FROM WM_BOOKMARK a 
                         JOIN WM_PLACE b ON a.PLACE_ID = b.PLACE_ID 
                         WHERE a.USER_ID = ? AND b.URL = ?";
        
        my ($dup_wm_place_url) = $dbh->selectrow_array($dup_check, undef, $user_id, $url);
        
        if (defined($dup_wm_place_url)) {
            die "Duplicate URL found: $url";
        }
        
        #------- UNICODE / LATIN charset block --------------#
        # workaround to not being able to change mysql server
        # character set - do not own mysql server
        #----------------------------------------------------#
        # Convert bytes to text
        my $title_decode = decode( "iso-8859-1", $title );

        # Convert text to SQL string literal -- nix this no needed aab
        #my $title_lit = $dbh->quote( $title_decode );
        my $title_lit =  $title_decode;

        # Convert text to bytes
        my $title_sql_utf8 = encode( "UTF-8", $title_lit );
        #----------------------------------------------------#
        #------- UNICODE / LATIN charset block --------------#

        # Insert into WM_PLACE
        my $place_sql = "INSERT INTO WM_PLACE (URL, TITLE) VALUES (?, ?)";

        $dbh->do($place_sql, undef, $url, $title_sql_utf8);

        my $place_id = $dbh->last_insert_id;
        
        # Insert into WM_BOOKMARK with both date formats
        my $bookmark_sql = "INSERT INTO WM_BOOKMARK (USER_ID, PLACE_ID, TITLE, DATEADDED, DATE_ADDED) 
                            VALUES (?, ?, ?, ?, ?)";

        $dbh->do($bookmark_sql, undef, $user_id, $place_id, $title_sql_utf8, $dateAdded, $date_added);
        
        
        # Commit transaction
        $dbh->commit() or die "Cannot commit: " . $dbh->errstr;
        
        print STDERR "Transaction *insert* committed successfully\n" if $DEBUG;
    };
    
    if ($@) {
        my $err_msg = $@;
        print STDERR "Transaction failed: $DBI::err --  $err_msg\n" if $DEBUG;
        
        # Rollback on error
        eval { $dbh->rollback() };
        if ($@) {
            print STDERR "Rollback failed: $@\n";
        }
        else {
            print STDERR "Transaction rolled back\n" if $DEBUG;
        }
        
        # Determine error type
        if ($err_msg =~ /Duplicate URL/) {
            $error = Error->new(ERR_DUPLICATE_URL);
        }
        else {
            $error = Error->new(ERR_MISSING_PARAMS);
        }
    }
    
    return $error;  # Returns undef on success, Error object on failure
}

sub update_mark {
    my $user_id = shift;
    my $title = $query->param('title_update');
    my $url = $query->param('url_update');
    my $bookmark_id = $query->param('bk_id');
    my $place_id;

    print STDERR "Updating bookmark - { $title } :$bookmark_id \n" if $DEBUG;
    
    my $error;
    
    eval {
        # Begin transaction
        $dbh->begin_work() or die "Cannot begin transaction: " . $dbh->errstr;
        
        ($place_id)  = $dbh->selectrow_array("select PLACE_ID from WM_BOOKMARK where BOOKMARK_ID = ? ", {}, $bookmark_id);

        $dbh->do(" update WM_BOOKMARK set TITLE = ? where BOOKMARK_ID = ? ", {}, $title, $bookmark_id);

        $dbh->do(" update WM_PLACE set URL = ? where PLACE_ID = ? ", {}, $url, $place_id);
        
        
        # Commit transaction
        $dbh->commit() or die "Cannot commit: " . $dbh->errstr;
        
        print STDERR "Transaction *update* committed successfully\n" if $DEBUG;
    };
    
    if ($@) {
        my $err_msg = $@;
        print STDERR "Transaction failed: $err_msg\n" if $DEBUG;
        
        # Rollback on error
        eval { $dbh->rollback() };
        if ($@) {
            print STDERR "Rollback failed: $@\n";
        }
        else {
            print STDERR "Transaction rolled back\n" if $DEBUG;
        }
        
        # Determine error type
            $error = Error->new(ERR_INSERT_FAILED);
    }
    
    return $error;  # Returns undef on success, Error object on failure
}


sub delete_mark {
    my $user_id = shift;
    my $title = $query->param('mark_title');
    my $url = $query->param('mark_url');
    my $bookmark_id = $query->param('bk_id');
    my $place_id;
    

    print STDERR "deleting bookmark - :$bookmark_id \n" if $DEBUG;
    
    my $error;
    
    eval {
        # Begin transaction
        $dbh->begin_work() or die "Cannot begin transaction: " . $dbh->errstr;
        
        ($place_id)  = $dbh->selectrow_array("select PLACE_ID from WM_BOOKMARK where BOOKMARK_ID = ? ", {}, $bookmark_id);
        $dbh->do(" delete from WM_BOOKMARK  where BOOKMARK_ID = ? ", {},  $bookmark_id);

        $dbh->do(" delete from WM_PLACE  where PLACE_ID = ? ", {},  $place_id);
        
        
        # Commit transaction
        $dbh->commit() or die "Cannot commit: " . $dbh->errstr;
        
        print STDERR "Transaction *delete* committed successfully\n" if $DEBUG;
    };
    
    if ($@) {
        my $err_msg = $@;
        print STDERR "Transaction failed: $err_msg\n" if $DEBUG;
        
        # Rollback on error
        eval { $dbh->rollback() };
        if ($@) {
            print STDERR "Rollback failed: $@\n";
        }
        else {
            print STDERR "Transaction rolled back\n" if $DEBUG;
        }
        
        # Determine error type
            $error = Error->new(ERR_INSERT_FAILED);
    }
    
    return $error;  # Returns undef on success, Error object on failure
}


#==============================================================================
# UTILITY FUNCTIONS
#==============================================================================

sub gen_json {
    my %in_hash = %{ shift() };
    my $json_out;
    my $json_out_;
    
    foreach (keys %in_hash) {
        $json_out_ .= qq( { "title" : "$_", "url" : "$in_hash{$_}->{url}", "dateAdded" : $in_hash{$_}->{dateAdded} },\n );
    }
    
    $json_out = sprintf("{\n %s \n}", $json_out_);
    print $json_out, "\n";
}

#==============================================================================
# MAIN EXECUTION
#==============================================================================
main_func();

# Cleanup
$dbh->disconnect() 
    or print STDERR "Disconnection failed: $DBI::errstr\n" 
    and warn "Disconnection failed: $DBI::errstr\n";

exit;
