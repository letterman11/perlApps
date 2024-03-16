#!/usr/bin/perl -wT

use strict;
#use lib "/services/webpages/d/c/dcoda.net/private/stockApp/script_src";
#use lib "/home/ubuntu/tools/perl5/site_perl";
use lib "/home/ubuntu/dcoda_net/lib";
use lib "/home/ubuntu/dcoda_net/private/stockApp/script_src";
require '/home/ubuntu/dcoda_net/cgi-bin/stockApp/cgi-bin/config.pl';
use lib "/home/abrooks/www/stockApp/script_src";
use StockUtil;
use GenModel;
use GenReport;
use GenError;
use CGI qw (:standard);
#use CGI::Carp qw(fatalsToBrowser);
=======
require '/home/abrooks/www/stockApp/cgi-bin/config.pl';


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
