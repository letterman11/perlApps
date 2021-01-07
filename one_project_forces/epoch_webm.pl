use strict;
use warnings;
use diagnostics;
 
use lib '/home/angus/dcoda_net/lib';
#use lib '/home/ubuntu/dcoda_net/lib';
use DbGlob;
use POSIX 'strftime';

our $configDb = "/home/angus/perlProjects/one_project/stockDbConfig.dat";
#our $configDb = "/home/ubuntu/perlProjects/one_project/stockDbConfig.dat";
our $urls_and_dates;

my $sth;
my @bind_vals_newDateAdded_urls;
my $mysql_date;
my $c = 0;

our $dbg = DbGlob->new($configDb);
our $dbh = $dbg->connect() or die "$!: $configDb";


my $sel_queryStr_1 =  qq/select b.URL, a.dateAdded from WM_BOOKMARK a, 
					WM_PLACE b where a.PLACE_ID = b.PLACE_ID /;

my $update_wm_bookmark_sql_1 =  qq/update WM_BOOKMARK a, WM_PLACE b 
								set a.DATE_ADDED = ? 
								where b.URL = ?
								and a.PLACE_ID = b.PLACE_ID /;

my $update_wm_bookmark_sql_21 =  qq/update WM_BOOKMARK 
								set DATE_ADDED = ? 
							    from WM_PLACE
								where  URL = ?
								and PLACE_ID = WM_PLACE.PLACE_ID /;

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

	$urls_and_dates = $sth->fetchall_arrayref();

   foreach(@$urls_and_dates) {

     #printf("%.35s\t%+25s\n", $_->[0], strftime "%Y-%m-%d %H:%M:%S", localtime(($_->[1])/(1000 * 1000)));
     $mysql_date  = strftime "%Y-%m-%d %H:%M:%S", localtime(($_->[1])/(1000 * 1000));
	 $_->[1] = $mysql_date;
  }

   foreach(@$urls_and_dates) {

     printf("%.35s\t%25s\n", $_->[0], $_->[1]);

   }


#=cut

   $dbh->trace(3);
   foreach(@$urls_and_dates) {

      #@bind_vals_newDateAdded_urls = ($dbh->quote($_->[1]), $dbh->quote($_->[0]));
      @bind_vals_newDateAdded_urls = ($_->[1], $_->[0]);

	  eval {	
   
		   $dbh->do($update_wm_bookmark_sql_1, {}, @bind_vals_newDateAdded_urls);

	  };

	  if ($@) {

		  print "Error update $!: $DbGlob::errstr\n";
	  }
	  else
	  {
		 print $c++, " Success\n";
	  }

   }
#=cut
 
