#!/usr/bin/perl -wT

############################################################################
#--------------- Initial checkin placeholder not useful for Ajax ----------#
############################################################################
use strict;
use lib "/home/abrooks/www/chatterBox/script_src";
use GenView;
use GenStatus;
use Error;
use GenError;
use Util;
use DbConfig;
use CGI qw /:standard/;
use CGI::Carp;
use DBI;
require '/home/abrooks/www/chatterBox/cgi-bin/config.pl';

$CGI::POST_MAX=1024 * 10;  # max 10K posts
$CGI::DISABLE_UPLOADS = 1;  # no uploads

my $query = new CGI;
my $callObj = ();

$callObj = Util::validateSession();
carp($callObj);

if (ref $callObj eq 'Error') {

	GenError->new($callObj)->display("Invalid form submission\n");
	exit;
}

$callObj =  Util::profileFormValidation($query);

if (ref $callObj eq 'Error') {
	GenError->new($callObj)->display("Invalid form submission\n");
	
} else {

	my $sqlHash = $callObj;

	my $dbconf = DbConfig->new();

	my $update_sql_str = ();

	if ($sqlHash->{new_password} && $sqlHash->{confirm_password}) {

		$update_sql_str .= "UPDATE user SET "
				.  " USER_PASSWD = '$sqlHash->{new_password}' "
				.  " WHERE USER_NAME = '$sqlHash->{userName}' ";

	} else {

		$update_sql_str .= "UPDATE user SET "
				.  " FNAME = '$sqlHash->{firstName}', "
				.  " LNAME = '$sqlHash->{lastName}', "
				.  " ADDRESS1 = '$sqlHash->{address1}', "
				.  " ADDRESS2 = '$sqlHash->{address2}', "
				.  " ZIP_CODE = $sqlHash->{zipcode}, "
				.  " PHONE = $sqlHash->{phone}, "
				.  " STATE = '$sqlHash->{state}', "
				.  " CITY = '$sqlHash->{city}' "
				.  " WHERE USER_NAME = '$sqlHash->{userName}' ";

	}


	carp ("$update_sql_str");

	my $dbh = DBI->connect( "dbi:mysql:"
	                . $dbconf->dbName() . ":"
	                . $dbconf->dbHost(),
	                  $dbconf->dbUser(),
	                  $dbconf->dbPass(), $::attr )
			  or GenError->new(Error->new(102))->display();
               
	eval {
	
		my $sth = $dbh->prepare($update_sql_str);
	
		$sth->execute();

		$dbh->disconnect();

	};

	#---- CGI header response ----#
	GenError->new(Error->new($DBI::err))->display("Application Error occurred try later\n") and die "$@" if ($@);

	GenStatus->new()->display("Update of profile successful for $sqlHash->{userName}\n");
}

exit;




