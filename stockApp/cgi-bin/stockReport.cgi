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

