#!/usr/bin/perl -wT

use strict;
use DBI;
use lib '/home/abrooks/www/pollCenter/script_src';
use DbConfig;
use CGI qw /:standard/;
use CGI::Carp;
use CGI::Cookie;
use Util;
use Captcha;
use Data::Dumper;
require '/home/abrooks/www/pollCenter/cgi-bin/config.pl';

my $pollCenterID;
my ($c1,$c2,$c3) = ();
my $sqlStr;
my $flagNewSession;
my $captcha_text;
my $captcha_parm;
my $q = new CGI;
my @parms = $q->param;
my $fh_client = $::PATHS->{CAPTCHA_DIR};
my $fh_serv = $::PATHS->{CAPTCHA_DIR_SERV};

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

   $fh_client .= "/$pollCenterID";
   $fh_serv .= "/$pollCenterID";

   mkdir ($fh_serv) or die "Cannot make dir: $fh_serv $!\n";

   $captcha_text = Captcha::genCaptcha($pollCenterID,$qID);    
 
   Util::storeSession($pollCenterID,
			$qID,
		        $captcha_text	
			);

   print $q->header( -status=> '200 OK',
   		-cookie=>[$c1,$c2],
	        -Content_Type=>'text/html'	
		);

   carp(Dumper($c1));
   carp(Dumper($c2));

   print STDOUT "$fh_client/$qID.png";
   
   carp("########## New Session  ############");
   carp(Dumper($q));   
   carp("####################################");
   
}
else
{
   $pollCenterID =  $initSessionObject->{POLLCENTERID};
   $captcha_text =  $initSessionObject->{CAPTCHA};
   $captcha_parm = $q->param('captcha_text');

   carp("from client: $captcha_parm / on server: $captcha_text");

   $fh_client .= "/$pollCenterID";

   if( defined $q->param('refresh')) 
   {
     
       carp("########### REFRESH ###########");
       $captcha_text = Captcha::genCaptcha($pollCenterID,$qID);    

       print $q->header( -status=> '200 OK',
                -cookie=>[$c2],
                -Content_Type=>'text/html'
                );

       print STDOUT "$fh_client/$qID.png";
         
   }
   elsif($captcha_parm eq $captcha_text)
   {
       exec_sql();
       $captcha_text = Captcha::genCaptcha($pollCenterID,$qID);    

       print $q->header( -status=> '200 OK',
                -cookie=>[$c2],
                -Content_Type=>'text/html'
                );

       print STDOUT "$fh_client/$qID.png";
         
   }
   else
   {
       print $q->header( -status=> '451 Captcha submission incorrect',
                -cookie=>[$c2],
                -Content_Type=>'text/html'
                );

       print STDOUT "Fouled up CAPTCHA submission";
   }

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
 
   my $dbconf = DbConfig->new();
    
   my $dbh = DBI->connect( "dbi:mysql:"
                    . $dbconf->dbName() . ":"
                    . $dbconf->dbHost(),
                    $dbconf->dbUser(),
                    $dbconf->dbPass(), $::attr )
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
