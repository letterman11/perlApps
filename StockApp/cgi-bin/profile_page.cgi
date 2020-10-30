#!/usr/bin/perl -wT

use strict;
use lib "/home/abrooks/www/stockApp/script_src";
use GenView;
use GenStatus;
use GenError;
use Error;
use StockUtil;
use GenProfile;
use DbConfig;
use CGI qw /:standard/;
use CGI::Carp qw(fatalsToBrowser);
use DBI;
require '/home/abrooks/www/stockApp/cgi-bin/config.pl';


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

	print header;
	GenProfile->new(\@profile_array)->display();

} else {

	GenError->new(Error->new(102))->display("Invalid form submission\n");
}

exit;

