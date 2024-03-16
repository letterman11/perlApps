#!/usr/bin/perl -wT

use strict;
<<<<<<< HEAD
use lib "/home/ubuntu/dcoda_net/stockApp/script_src";
=======
use lib "/home/ubuntu/dcoda_net/private/stockApp/script_src";
>>>>>>> 159a4bd (modified stockApp cgi files)
use GenView;
use GenHome;
use GenLogin;
use StockUtil;
use DbConfig;
use CGI qw /:standard/;
use CGI::Cookie;
use CGI::Carp qw(fatalsToBrowser);
use DBI;
<<<<<<< HEAD
require '/home/ubuntu/dcoda_net/stockApp/cgi-bin/config.pl';
=======
require '/home/ubuntu/dcoda_net/cgi-bin/stockApp/cgi-bin/config.pl';
>>>>>>> 159a4bd (modified stockApp cgi files)



my $userID = 0;
my $userName = 1;
my $userPass = 2;
my $startpage="/home/ubuntu/dcoda_net/stockApp/web_src/stockapp.html";
my $query = new CGI;
my $host = $::GLOBALS->{HOST}; # !!! change for production server to dcoda.net

my $dbconf = DbConfig->new();
my $dbh = DBI->connect( "dbi:mysql:"  
		. $dbconf->dbName() . ":"
		. $dbconf->dbHost(), 
		$dbconf->dbUser(), 
		$dbconf->dbPass(), $::attr )
        	or die "Cannot Connect to Database $DBI::errstr\n";

my $user_name = $query->param('userName');
my $user_pass = $query->param('userPass');

my $sqlstr = "select USER_ID, USER_NAME, USER_PASSWD from user "
		. " where USER_NAME = '" 
		. $user_name . "' and  USER_PASSWD = '" . $user_pass .  "'";
  
my $sth = $dbh->prepare($sqlstr);
$sth->execute();

my @user_row = $sth->fetchrow_array();
$sth->finish();

$dbh->disconnect();

if (not defined ($user_row[1])) {
	GenLogin->new()->display("Invalid User Name/ <br> Password combination\n");	
} else
{
	my $stockSessionID = StockUtil::genSessionID();

	my $sessionInstance = "ses1";

	my $c1 = new CGI::Cookie(-name=>'stock_SessionID',
			-value=>$stockSessionID,
			-expires=>undef, 
			-domain=>$host,  
			-path=>'/');

	my $c2 = new CGI::Cookie(-name=>'stock_UserID',
			-value=>$user_name,
			-expires=>undef, 
			-domain=>$host, 
			-path=>'/');

	my $c3 = new CGI::Cookie(-name=>'Instance',
			-value=>$sessionInstance,
			-expires=>undef, 
			-domain=>$host,  
			-path=>'/');


	StockUtil::storeSession($sessionInstance,
				$stockSessionID, 
				$user_row[$userName]);


	GenHome->new([$c1,$c2,$c3])->display();

}

