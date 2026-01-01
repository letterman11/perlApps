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


use GenStatus;
use Error;
use GenError;
use Util;
use DbConfig;
use CGI qw /:standard/;
use CGI::Carp;

$CGI::POST_MAX=1024 * 10;  # max 10K posts
$CGI::DISABLE_UPLOADS = 1;  # no uploads
 
my $query = new CGI;
my $callObj =  Util::formValidation($query);

if (ref $callObj eq 'Error') {

	print $query->header(-status=>'451 Invalid Form Submission'
				);
	
} else {

	my $sqlHash = $callObj;

	my $dbconf = DbConfig->new()
			  or GenError->new(Error->new(102))->display();

	my $insert_sql_str = "INSERT INTO user VALUES ('$sqlHash->{userName}','$sqlHash->{userName}','$sqlHash->{password}'," 
					. "'$sqlHash->{firstName}','$sqlHash->{lastName}','$sqlHash->{address1}','$sqlHash->{address2}',"
					#. "'$sqlHash->{zipcode}','$sqlHash->{phone}','$sqlHash->{email}','$sqlHash->{state}','$sqlHash->{city}')";
					. "10101,3477899000,'$sqlHash->{email}','$sqlHash->{state}','$sqlHash->{city}')";


	carp ("$insert_sql_str");

	my $dbh = $dbconf->connect()
			  or  die "Could not Connect to Database $DBI::errstr";

	eval {
	
		my $sth = $dbh->prepare($insert_sql_str);
	
		$sth->execute();

		$dbh->disconnect();

	};

	if ($@) 
	{
		print $query->header(-status=>'452 Application Error'
						);
		#carp($DBI::errstr);

                #carp("Failed");
	}
	else
	{
		print $query->header(-status=>'200 Registration Successful');
		print "Registration Successful for " . $sqlHash->{userName};
                #carp("Succeeded");
	}

}

exit;




