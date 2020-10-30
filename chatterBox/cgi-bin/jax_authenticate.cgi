#!/usr/bin/perl -wT

use strict;
#use lib "/services/webpages/d/c/dcoda.net/private/chatterBox/script_src";
#use lib "/home/angus/dcoda_net/lib";
use lib "/home/angus/dcoda_net/private/chatterBox/script_src";
require "/home/angus/dcoda_net/cgi-bin/chatterBox/cgi-bin/config.pl";
use Util;
use DbConfig;
use CGI qw /:standard/;
use CGI::Cookie;
use CGI::Carp qw(fatalsToBrowser);


$CGI::POST_MAX=1024 * 10;  # max 10K posts
$CGI::DISABLE_UPLOADS = 1;  # no uploads

my $userID = 0;
my $userName = 1;
my $userPass = 2;
my $startpage="/home/abrooks/www/chatterBox/web_src/chatterapp.html";
my $query = new CGI;

#my $host = $::GLOBALS->{HOST}; # !!! change for production server to dcoda.net
#my $host = "pyperl-bluelimit.c9users.io";

my $host = undef;

my $dbc = DbConfig->new()
        	or die "Cannot Create  Handle \n";

my $dbh = $dbc->connect()
        	or die "Cannot create connection to Database $DBI::errstr \n";

my $user_name = $query->param('userName');
my $user_pass = $query->param('userPass');

my $sqlstr = "select USER_ID, USER_NAME, USER_PASSWD from user "
		. " where USER_NAME = '" 
		. $user_name . "' and  USER_PASSWD = '" . $user_pass .  "'";

my $sth;

eval {  

  $sth = $dbh->prepare($sqlstr);
  $sth->execute();

};
    carp "sqlout : $sqlstr\n";

if ($@) {

    carp "FAILURE : $sqlstr\n";

}

my @user_row = $sth->fetchrow_array();
$sth->finish();



$dbh->disconnect();

#if ($user_row[1] =~ /^\s*\t*$/) {

if (not defined ($user_row[1])) {

	#---- CGI header response ----#
	print $query->header(-status=>'401 Invalid UserID/Password Entry');	
        print "Failed Authorization\n";
	carp("Another failure ack");

} else
{

	my $SessionID = Util::genSessionID();

	my $sessionInstance = "ses1";

	my $c1 = new CGI::Cookie(-name=>'chatSessionID',
			-value=>$SessionID,
			-expires=>undef, 
			-domain=>$host,
			-path=>'/');

	my $c2 = new CGI::Cookie(-name=>'chatUserID',
			-value=>$user_name,
			-expires=>undef, 
			-domain=>$host,
			-path=>'/');

	my $c3 = new CGI::Cookie(-name=>'Instance',
			-value=>$sessionInstance,
			-expires=>undef, 
			-domain=>$host,
			-path=>'/');


	Util::storeSession($sessionInstance,
				$SessionID, 
				$user_row[$userName]);

	#---- CGI header response ----#
	print $query->header(-status=>200,
			     -cookie=>[$c1,$c2,$c3]
			    );

}

exit;
