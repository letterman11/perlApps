#!/usr/bin/perl -wT

use strict;
use lib "/home/ubuntu/dcoda_net/lib";
use lib "/home/ubuntu/dcoda_net/private/stockApp/script_src";
require '/home/ubuntu/dcoda_net/cgi-bin/stockApp/cgi-bin/config.pl';
use StockUtil;
use GenModel;
use GenReport;
use CGI qw (:standard);
use CGI::Carp qw(fatalsToBrowser);


my $sessInst = ();
my $sessID = ();
my $userID = ();
my $initSessionObject = ();
my $query = new CGI;
my %params = $query->Vars;

$initSessionObject = StockUtil::validateSession();

if (ref $initSessionObject eq 'SessionObject') { 

       $sessInst = $initSessionObject->{INSTANCE};
       $sessID =  $initSessionObject->{SESSIONID};
    
       my $model = GenModel->new(\%params);
    
       $model->genSQL();
       my ($data, $rowcount, $sort) = $model->execIndexQuery();
       my $sessionObject = SessionObject->new($sessInst,
    					 $sessID,
    					 $data,
    					 $rowcount,
					 $sort);
    
       StockUtil::storeSessionObject($sessionObject);
    
       $model->genSQL($sessionObject);

       $model->execQuery();

       my $view = GenReport->new($model);

       $view->display();


} else {
 
	GenError->new(Error->new(104))->display();

}

