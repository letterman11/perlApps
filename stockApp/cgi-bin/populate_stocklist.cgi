#!/usr/bin/perl -wT

use strict;

use FindBin qw($Bin);
our $untainted_bin;

BEGIN {
    # Extract the trusted part of $Bin using a regular expression
    # This assumes $Bin contains a valid path and removes any potentially malicious characters.
    ($untainted_bin) = $Bin =~ /^(.+)$/;
}


#use lib "/home/ubuntu/dcoda_net/lib";
use lib "$untainted_bin/../../../private/stockApp/script_src";
require "$untainted_bin/config.pl";

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

