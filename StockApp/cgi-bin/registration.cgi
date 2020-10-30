#!/usr/bin/perl -wT

use strict;
use lib "/home/abrooks/www/stockApp/script_src";
use GenView;
use GenStatus;
use Error;
use GenError;
use StockUtil;
use DbConfig;
use CGI qw /:standard/;
#use CGI::Carp qw(fatalsToBrowser);
use CGI::Carp;
use DBI;
require '/home/abrooks/www/stockApp/cgi-bin/config.pl';

 
my $query = new CGI;
my $callObj =  StockUtil::formValidation($query);

if (ref $callObj eq 'Error') {
	GenError->new($callObj)->display("Invalid form submission\n");
	
} else {

	my $sqlHash = $callObj;

	my $dbconf = DbConfig->new();

	my $insert_sql_str = "INSERT INTO user VALUES ('$sqlHash->{userName}','$sqlHash->{userName}','$sqlHash->{password}'," 
					. "'$sqlHash->{firstName}','$sqlHash->{lastName}','$sqlHash->{address1}','$sqlHash->{address2}',"
					. "'$sqlHash->{zipcode}','$sqlHash->{phone}','$sqlHash->{email}','$sqlHash->{state}','$sqlHash->{city}')";


	carp ("$insert_sql_str");

	my $dbh = DBI->connect( "dbi:mysql:"
	                . $dbconf->dbName() . ":"
	                . $dbconf->dbHost(),
	                  $dbconf->dbUser(),
	                  $dbconf->dbPass(), $::attr )
			  or GenError->new(Error->new(102))->display();
               
	eval {
	
		my $sth = $dbh->prepare($insert_sql_str);
	
		$sth->execute();

		$dbh->disconnect();

	};

	GenError->new(Error->new($DBI::err))->display("Application Error occurred try later\n") and die "$@" if ($@);

	GenStatus->new()->display("Registration successful for $sqlHash->{userName}\n");
}

exit;




