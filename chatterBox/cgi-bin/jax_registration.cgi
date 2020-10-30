#!/usr/bin/perl -wT


use strict;
#use lib "/services/webpages/d/c/dcoda.net/private/chatterBox/script_src";
#use lib "/home/ubuntu/tools/perl5/site_perl";
#use lib "/home/angus/dcoda_net/lib";
use lib "/home/angus/dcoda_net/private/chatterBox/script_src";
require '/home/angus/dcoda_net/cgi-bin/chatterBox/cgi-bin/config.pl';
use GenStatus;
use Error;
use GenError;
use Util;
use DbConfig;
use CGI qw /:standard/;
use CGI::Carp;
#use CGI::Carp qw(fatalsToBrowser);
#use DBI;
#require '/services/webpages/d/c/dcoda.net/cgi-bin/chatterBox/cgi-bin/config.pl';

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




