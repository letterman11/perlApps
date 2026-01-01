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

#use lib "/home/ubuntu/dcoda_net/lib";

use GenView;
use GenHome;
use StockUtil;
use CGI qw /:standard/;
use CGI::Cookie;

use CGI::Carp qw(fatalsToBrowser);
use DbConfig;

my $host=undef;

my $initSessionObj = StockUtil::validateSession();

if (ref $initSessionObj ne 'SessionObject')
{

   my $stockSessionID = StockUtil::genSessionID();
    
   my $sessionInstance = "ses1";

   my $c1 = new CGI::Cookie(-name=>'stockUserID',
                -value=>'stockUser',
                -expires=>undef,
		-path=>'/');
    
   my $c2 = new CGI::Cookie(-name=>'stockSessionID',
    		-value=>$stockSessionID,
    		-expires=>undef,
		-path=>'/');
    
   StockUtil::storeSession($sessionInstance,
    			$stockSessionID, 
    			'stockUser');
    
   GenHome->new([$c1,$c2])->display();
   
} 
else
{  
   GenHome->new()->display();
} 
