use strict;
use English;
use warnings;
use diagnostics;
 
use lib '/home/angus/dcoda_net/lib';
use DbGlob;
use POSIX 'strftime';

our $configDb = "/home/angus/perlProjects/one_project/stockDbConfig.dat";
our $urls_and_dates_placeIds;

my $sth;
my @bind_vals_newDateAdded_urls_placeIds;
my $mysql_date;
my $c = 0;

our $dbg = DbGlob->new($configDb);
our $dbh = $dbg->connect() or die "$!: $configDb";


my $sel_queryStr_1 =  qq#
select b.URL, a.dateAdded, b.place_id from WM_BOOKMARK a, 
WM_PLACE b where a.PLACE_ID = b.PLACE_ID; #;


my $update_wm_bookmark_sql_1 =  qq/update WM_BOOKMARK a, WM_PLACE b 
								set a.DATE_ADDED = ? 
								where b.URL = ?
								and a.PLACE_ID = b.PLACE_ID /;

my $update_wm_bookmark_sql_21 =  qq/update WM_BOOKMARK 
								set DATE_ADDED = ? 
								where PLACE_ID = ? /;
										
my $update_wm_bookmark_sql_22 =  qq/update WM_BOOKMARK 
								set DATE_ADDED = ? 
								where PLACE_ID = ? /;
										

   eval {
	    $sth = $dbh->prepare($sel_queryStr_1);

		$sth->execute();


	};

	if ($@)
	{
		print "Error  $DbGlob::errstr\n";
		exit(22);
	}
	else
	{

		print "Success\n";
	}

	$urls_and_dates_placeIds = $sth->fetchall_arrayref();

   foreach(@$urls_and_dates_placeIds) {

     $mysql_date  = strftime "%Y-%m-%d %H:%M:%S", localtime(($_->[1])/(1000 * 1000));
	 $_->[1] = $mysql_date;
  }

   foreach(@$urls_and_dates_placeIds) {

     printf("%.35s\t%25s%15s\n", $_->[0], $_->[1], $_->[2]);

   }


   foreach(@$urls_and_dates_placeIds) {

      #@bind_vals_newDateAdded_urls_placeIds = ($_->[1], $_->[0], $_->[2]);
      @bind_vals_newDateAdded_urls_placeIds = ($_->[1], $_->[2]);

	  eval {	
   
		   $dbh->do($update_wm_bookmark_sql_22, {}, @bind_vals_newDateAdded_urls_placeIds);
			
	  };

	  if ($@) {

		  print "Error update $!: $DbGlob::errstr\n";
	  }
	  else
	  {
		 print $c++, " Success\n";
	  }

   }
