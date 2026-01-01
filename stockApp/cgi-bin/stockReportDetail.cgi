#!/usr/bin/perl -wT

use strict;

use FindBin qw($Bin);
our $untainted_bin;

BEGIN {
    # Extract the trusted part of $Bin using a regular expression
    # This assumes $Bin contains a valid path and removes any potentially malicious characters.
    ($untainted_bin) = $Bin =~ /^(.+)$/;
}


use lib "$untainted_bin/../../../private/stockApp/script_src";
require "$untainted_bin/config.pl";
#use lib "/home/ubuntu/dcoda_net/lib";

use StockUtil;
use GenModel;
use GenReport;
use GenError;
use CGI qw (:standard);
#use CGI::Carp qw(fatalsToBrowser);


my $callObj = ();
my $sessInst = ();
my $sessID = ();
my $query = new CGI;
my %params = $query->Vars;

($callObj) = StockUtil::validateSession();


if (ref $callObj eq 'SessionObject') 
{ 
  
   my $model = GenModel->new(\%params);

   $model->genSQL($callObj);

   $model->execQuery(); 

   my $view = GenReport->new($model);

   $view->display($query->param('page'));

} 
else 
{
    GenError->new(Error->new(104))->display();
}
