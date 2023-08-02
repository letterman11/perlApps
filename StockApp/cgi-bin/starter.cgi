#!/usr/bin/perl -wT

use strict;
use lib "/home/ubuntu/dcoda_net/stockApp/script_src";
use GenView;
use GenHome;
use StockUtil;
use CGI qw /:standard/;
use CGI::Cookie;
#use CGI::Carp qw(fatalsToBrowser);
require '/home/ubuntu/dcoda_net/stockApp/cgi-bin/config.pl';

my $initSessionObj = StockUtil::validateSession();

if (ref $initSessionObj ne 'SessionObject')
{

   my $stockSessionID = StockUtil::genSessionID();
    
   my $sessionInstance = "ses1";

   my $c1 = new CGI::Cookie(-name=>'stockUserID',
                -value=>'stockUser',
                -expires=>undef,
		-path=>'/stockApp');
    
   my $c2 = new CGI::Cookie(-name=>'stockSessionID',
    		-value=>$stockSessionID,
    		-expires=>undef,
		-path=>'/stockApp');
    
   StockUtil::storeSession($sessionInstance,
    			$stockSessionID, 
    			'stockUser');
    
   GenHome->new([$c1,$c2])->display();
   
} 
else
{  
   GenHome->new()->display();
} 
