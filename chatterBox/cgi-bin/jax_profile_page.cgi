#!/usr/bin/perl -wT

############################################################################
#--------------- Initial checkin placeholder not useful for Ajax ----------#
############################################################################
use strict;
use lib "/home/abrooks/www/chatterBox/script_src";
use GenError;
use Error;
use Util;
use DbConfig;
use CGI qw /:standard/;
use CGI::Carp qw(fatalsToBrowser);
use DBI;
require '/home/abrooks/www/chatterBox/cgi-bin/config.pl';

$CGI::POST_MAX=1024 * 10;  # max 10K posts
$CGI::DISABLE_UPLOADS = 1;  # no uploads

my @profile_array;
my $query = new CGI;
my $user_name = $query->param('userName');

if (defined($user_name) && ($user_name !~ /^\s*$/)) {

	my $dbconf = DbConfig->new();

	my $select_sql_str = "SELECT user_name, fname, lname, address1, address2," 
					. " zip_code, phone, email_address, state, city "
					. " FROM user WHERE user_name = '" . $user_name . "'"; 
	carp ("$select_sql_str");

	my $dbh = DBI->connect( "dbi:mysql:"
	                . $dbconf->dbName() . ":"
	                . $dbconf->dbHost(),
	                  $dbconf->dbUser(),
	                  $dbconf->dbPass(), $::attr )
			  or GenError->new(Error->new(102))->display();
               
	eval {
	
		my $sth = $dbh->prepare($select_sql_str);
	
		$sth->execute();

		@profile_array = $sth->fetchrow_array;

		$sth->finish();

		$dbh->disconnect();

	};

	GenError->new(Error->new(102))->display("Application Error occurred try again later\n") and die "$@" if ($@);
	#---- CGI header response ----#	

} else {

	GenError->new(Error->new(102))->display("Invalid form submission\n");
	#---- CGI header response ----#
}

exit;

