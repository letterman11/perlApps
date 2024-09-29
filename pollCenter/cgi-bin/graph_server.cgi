#!/usr/bin/perl -wT

use strict;
use DBI;
#use lib "/home/ubuntu/tools/perl5/site_perl";
use lib "/home/ubuntu/dcoda_net/private/pollCenter/script_src";
require '/home/ubuntu/dcoda_net/cgi-bin/pollCenter/cgi-bin/config.pl';
use lib "/home/ubuntu/dcoda_net/lib";
#use lib "/services/webpages/d/c/dcoda.net/private/pollCenter/script_src";
#use DbConfig;
use DbGlob;
use CGI qw /:standard/;
use CGI::Carp;
use Util;
use Data::Dumper;

my $JSON;
my $q = new CGI;
my $initSessionObject = Util::validateSession('pollCenterID','qID');

if (ref $initSessionObject eq 'SessionObject') 
{
    
   my $pollIDparm = $q->param('poll_ids');
   carp("############ $pollIDparm ###################");

   if (defined($pollIDparm))
   {
    
	   #my $dbconf = DbConfig->new();
	   my $dbg = DbGlob->new("stockDbConfig.dat");

	   my $dbh = $dbg->connect()
	                or die "Cannot Connect to Database $DBI::errstr\n";
       
       $JSON = " [ ";

       my @a = ();
       for my $pollID (split(":", $pollIDparm))
       {
        
           carp("########## pollID - $pollID - pollID ##############");
           my @row_array  = $dbh->selectrow_array("select * from poll where poll_id = $pollID");
           ## add exception logic#
           #######################

           my $pollObj = genJSON(\@row_array);
	   #$JSON .= $pollObj . ", ";
	  $a[++$#a] = $pollObj;
       }
      
       $JSON .= $a[0] . " ";;  

       for(my $i=1; $i < scalar(@a); $i++)
       {
	   $JSON .= "," . $a[$i]; 
       }
       
      $JSON .= " ]  ";

   }         

   print $q->header( -status=> '200 OK',
		-Content_Type=>'application/json');

   print $JSON;

   carp("######## JSON OUT ################");
   print STDERR $JSON;
   carp("######## JSON OUT ################");

}


sub genJSON
{

   ##  JSON parsing of property - renderer:$.jqplot.BarRenderer not handled well client side even with escapes
   ##  will reset explicit on client side.
   my @row_data = @{(shift)};
   my ($poll_id,$poll_desc,$poll_optionslist,$poll_optlistflag,$category_id,$creation_ts) = (0..4,25); 

   my $jsJQPlotBarColors = " \"seriesColors\" : [ \"orange\", \"#c5b47f\", \"#EAA228\", \"#579575\", \"#839557\" ]";
  # my $jsJQPlotBarColors = qq{  'seriesColors' : [ 'orange', 'blue', 'orange', 'red', 'brown' ] };
#   my $jsJQPlotBarColors = qq { "seriesColors" : [ "undef" ] };

   #my $jsJQPlotSeriesDefs = " \"series\": { \"pointLabels\": { \"show\": true }, \"seriesDefaults\" : { 					 \	
   my $jsJQPlotSeriesDefs =  "\"seriesDefaults\" : { 					 \	
                                                   \"renderer\" : \"\$.jqplot.BarRenderer\",	 \	
                                         	   \"markerOptions\" : { },\
						  \"pointLabels\": { \"show\": false }, \
                                                   \"rendererOptions\" : { \"barWidth\" : null, \"barPadding\": 8 } 	\	
                                               }";

   my $jsJQPlotAxes = " \"axes\" : { 					\
                  	             \"xaxis\" : {				\
					   \"renderer\":\"\$.jqplot.CategoryAxisRenderer\", \
                                         \"tickOptions\" : { \"show\": true,\"autoscale\":true },	\
                                         \"showLabel\" : true,		\
                                         \"showTicks\" : false,		\
                                         \"showTickMarks\" : false		\
                                        },				\
				     \"yaxis\" : { 		\
                                         \"tickOptions\" : { },	\
					  \"min\": 0, \
					  \"numberTicks\": 10\
				      } \
                         }";

   my $jsJQPlotLegend = "  \"legend\" : {			\
                                       \"show\" : false,	\
                                       \"showLabels\" : true,	\
                                       \"location\" : \"ne\",	\
                                       \"placement\" : \"outside\"	\
                                   }";


   ### for getting names and values of poll options
   my $colShiftNames = 5; 
   my $colShiftVals = 15; 

   my %pollDataHash = ();

   for(my $i=0; $i < 10; $i++)
   {
       if(defined($row_data[$colShiftNames + $i]))	  
       {
           $pollDataHash{$row_data[$colShiftNames + $i]} = $row_data[$colShiftVals + $i]; 
       } 
       else
       {
	   last;
       }

   }

   ### JS overrides gen for JqPlot ###
   my @pollOption = (sort keys %pollDataHash); 

#   my $seriesOverRides = qq/ "series" : [ { "showLabels" : true }, /;
   my $seriesOverRides = qq/ "series" : [  /;
#   my $seriesOverRides = " \"series\" : [\n \t\t {\"pointLabels\": { \"show\": true } ] \n ";

#   $seriesOverRides .= " { \"label\" : \"" . $pollOption[0] . "\" } ";
#
#   $seriesOverRides .= " { \"label\" : \"" . $pollOption[0] . "\" } ";
#   $seriesOverRides .= " { \"label\" : \"" . $pollOption[0] . "\" } ";
#   $seriesOverRides .= "  , $pollOption[0] . "\" } ";
#         
#  labels:['fourteen', 'thirty two', 'fourty one', 'fourty four', 'fourty'] 



#
#   for (my $i=1; $i < scalar(@pollOption); $i++)
#   {
#       $seriesOverRides .= ", { \"label\" : \"" . $pollOption[$i] . "\" } ";
#   }
# $seriesOverRides .= " ]";
#pointLabels:{
#        show: true,
   $seriesOverRides .= qq/ { "pointLabels": { "show": true, "labels" : [ "$pollOption[0]" / ;
#   $seriesOverRides .= "  , $pollOption[0] . "\" } ";
   for (my $i=1; $i < scalar(@pollOption); $i++)
   {
       $seriesOverRides .= qq/, "$pollOption[$i]" /;
   }

   $seriesOverRides .= "  ] }} ]";

   ### JS data array gen for JqPlot ### 
   my $seriesData = " [ [";

   my @pollKeyData = (sort keys %pollDataHash);

   $seriesData .= " "  . $pollDataHash{$pollKeyData[0]} . " "; 
   #$seriesData .= qq/ "$pollOption[0]", $pollDataHash{$pollKeyData[0]}] /; 

   for(my $i=1; $i < scalar(@pollKeyData); $i++)
   {
       $seriesData .= ", " . $pollDataHash{$pollKeyData[$i]} . " ";
       #$seriesData .= qq/,["$pollOption[$i]",  $pollDataHash{$pollKeyData[$i]}] /;
   } 

   $seriesData .= " ] ] ";
   #$seriesData .= "  ] ";

   #my $optionsObj = sprintf("{%s,\n%s,\n%s,\n%s,\n%s\n}",
   my $optionsObj = sprintf("{\n%s,\n%s,\n%s,\n%s\n}",
			#$jsJQPlotBarColors,$jsJQPlotSeriesDefs,$jsJQPlotLegend,
			$jsJQPlotSeriesDefs,$jsJQPlotLegend,
							$jsJQPlotAxes,$seriesOverRides);

   my $pollObj = sprintf("{\n \"data\" :  %s,\n \"options\" :\n\t%s\n}\n",$seriesData,$optionsObj);    

   return $pollObj;

}
#   varyBarColor: true

exit;
