#!/usr/bin/perl -wT

use strict;
#use lib "/home/angus/dcoda_net/lib";
use lib "/home/angus/dcoda_net/private/stockApp/script_src";
require '/home/angus/dcoda_net/cgi-bin/stockApp/cgi-bin/config.pl';
use GenError;
use Error;
use GenStockList;
use DbConfig;
use CGI qw /:standard/;
use CGI::Carp qw(fatalsToBrowser);

my $stocklist = ();
my @stocklist_array;
my $query = new CGI;

 
my $dbc = DbConfig->new();

my $select_sql_str = "SELECT DISTINCT stock_symbol FROM orders"; 
#carp ("$select_sql_str");

my $dbh = $dbc->connect()
		  or GenError->new(Error->new(102))->display() and die;

eval {

	my $sth = $dbh->prepare($select_sql_str);

	$sth->execute();

	while( ($stocklist) = $sth->fetchrow_array ) {
		push @stocklist_array, $stocklist;

	}

	$sth->finish();

	$dbh->disconnect();

};

	GenError->new(Error->new(102))->display() and die "$@" if ($@);

	#carp ("@stocklist_array");
	print header;
	GenStockList->new(\@stocklist_array)->display();



exit;

