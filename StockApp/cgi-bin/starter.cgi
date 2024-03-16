#!/usr/bin/perl -wT

use strict;
use lib "/home/ubuntu/dcoda_net/private/stockApp/script_src";
#use lib "/home/ubuntu/tools/perl5/site_perl";
#use lib "/home/ubuntu/tools/perl5/site_perl";
use lib "/home/ubuntu/dcoda_net/lib";
###############
use lib "/home/ubuntu/dcoda_net/private/stockApp/script_src";
require '/home/ubuntu/dcoda_net/cgi-bin/stockApp/cgi-bin/config.pl';

use GenView;
use GenHome;
use GenError;
use StockUtil;
use CGI qw /:standard/;
use CGI::Cookie;
#use CGI::Carp qw(fatalsToBrowser);
require '/home/ubuntu/dcoda_net/cgi-bin/stockApp/cgi-bin/config.pl';
use CGI::Carp qw(fatalsToBrowser);
use DbConfig;

#my $host="pyperl-bluelimit.c9users.io";
my $host=undef;

my $initSessionObj = StockUtil::validateSession();
my ($c1,$c2) = ();


if (ref $initSessionObj ne 'SessionObject')
{

   my $stockSessionID = StockUtil::genSessionID();
    
   my $sessionInstance = "ses1";

   $c1 = new CGI::Cookie(-name=>'stockUserID',
                -value=>'stockUser',
    		-domain=>$host,
                -expires=>undef,
		-path=>'/');
    
   $c2 = new CGI::Cookie(-name=>'stockSessionID',
    		-value=>$stockSessionID,
    		-domain=>$host,
    		-expires=>undef,
		-path=>'/');
    
   StockUtil::storeSession($sessionInstance,
    			$stockSessionID, 
    			'stockUser');
    
   GenHome->new([$c1,$c2])->display();
   
} 
else
{   
   GenHome->new([$c1,$c2])->display();
} 
