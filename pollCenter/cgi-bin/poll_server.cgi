#!/usr/bin/perl -wT

use strict;
use DBI;
#use lib "/home/angus/tools/perl5/site_perl";
use lib "/home/angus/dcoda_net/private/pollCenter/script_src";
require '/home/angus/dcoda_net/cgi-bin/pollCenter/cgi-bin/config.pl';
#use lib "/services/webpages/d/c/dcoda.net/private/pollCenter/script_src";
#use DbConfig;
use DbGlob;
use CGI qw /:standard/;
use CGI::Carp;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
use Util;
#use Captcha;

use Data::Dumper;
#require '/services/webpages/d/c/dcoda.net/cgi-bin/pollCenter/cgi-bin/config.pl';

my $pollCenterID;
my ($c1,$c2,$c3) = ();
my $sqlStr;
my $flagNewSession;
my $captcha_text = "none";
my $captcha_parm;
my $q = new CGI;
my @parms = $q->param;
#my $fh_client = $::PATHS->{CAPTCHA_DIR};
#my $fh_serv = $::PATHS->{CAPTCHA_DIR_SERV};

my $initSessionObject = Util::validateSession('pollCenterID','qID');

my $qID = Util::genQueryID();
   
if (ref $initSessionObject ne 'SessionObject') 
{
   $pollCenterID = Util::genSessionID();
    
   $c1 = new CGI::Cookie(-name=>'pollCenterID',
        -value=>$pollCenterID,
        -expires=>undef,
        -domain=>undef,
         -path=>'/');

   $c2 = new CGI::Cookie(-name=>'qID',
        -value=>$qID,
        -expires=>undef,
        -domain=>undef,
         -path=>'/');
 
   Util::storeSession($pollCenterID,
			$qID,
		        $captcha_text	
			);

   print $q->header( -status=> '200 OK',
   		-cookie=>[$c1,$c2],
	        -Content_Type=>'text/html'	
		);

   #carp(Dumper($c1));
   #carp(Dumper($c2));

   
   #carp("########## New Session  ############");
   carp(Dumper($q));   
  # carp("####################################");
   
}
else
{
   $pollCenterID =  $initSessionObject->{POLLCENTERID};
   $captcha_text =  $initSessionObject->{CAPTCHA};

#   if( defined $q->param('refresh')) 
#   {
     
       exec_sql();

       print $q->header( -status=> '200 OK',
                -cookie=>[$c2],
                -Content_Type=>'text/html'
                );

         
#   }

   Util::storeSession($pollCenterID,
			$qID,
		        $captcha_text	
			);

   carp("########## Session Already ############");
   carp(Dumper($q));   
   carp("#######################################");

}

carp($qID);
carp(Dumper($initSessionObject));
 
   
sub exec_sql
{
 
	my $dbg = DbGlob->new("stockDbConfig.dat");
	#my $dbconf = DbConfig->new();
    
	my $dbh = $dbg->connect()
	       or die "Cannot Connect to Database $DBI::errstr\n";

   $sqlStr = 'update poll set ';
    
   for my $parm (@parms)
   {
       if ($parm =~ /poll_id/) 
       {
         ############################## string extraction ############################
    
           my $OptionChoice = $q->param($parm);
           my $pollIdVal = substr($parm,7,10); 
    
           my $pollOptionChoice = "poll_optioncount$OptionChoice";
    
           my @row_array  = $dbh->selectrow_array("select $pollOptionChoice from poll where poll_id = $pollIdVal");
           ## add exception logic#
           #######################
           
           my $newCountTotal = $row_array[0];
           $newCountTotal = 0 if not defined $newCountTotal; 
           $newCountTotal++;
    
           my $sqlStr1 .= $sqlStr    
           . " $pollOptionChoice = $newCountTotal "
           . " where poll_id = $pollIdVal "; 
    
          carp($sqlStr1);
    
          my $rc = $dbh->do($sqlStr1);
          ## add exception logic#
          #######################
    
         ############################## string extraction ############################
           carp("$pollIdVal \t $OptionChoice");
    
       }
    
   }
        
}


exit;
