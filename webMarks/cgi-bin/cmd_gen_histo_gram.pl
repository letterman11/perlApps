#!/usr/bin/perl -w

use strict;
use lib "/home/ubuntu/tools/perl5/site_perl";
use lib "/home/ubuntu/workspace/dcoda_net/private/webMarks/script_src";

use globals;
use DbConfig;
use DBD::SQLite;
use CGI qw (:standard);

my @H = ();
my $dbconf = DbConfig->new();
my $dbh = DBI->connect( "dbi:SQLite:dbname="
                . $dbconf->dbName() . ""
                . $dbconf->dbHost(),
                $dbconf->dbUser(),
                $dbconf->dbPass(), $::attr )
                or die "Cannot Connect to Database $DBI::errstr\n";

#my $hist_sql_str = "select b.url, a.title, a.dateAdded from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID and a.USER_ID = ?  "; 
my $hist_sql_all_str = "select b.url, a.title, a.dateAdded from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID "; 


sub gen_histogram
{
	my %markHist = ();
	my %elimdups = ();
	my @histo_list = ();	
	my ($title,$url,$dateAdded) = (1,0,2);

	### error checking ????? ##############
	my $sth = $dbh->prepare($hist_sql_all_str);
	#my $sth = $dbh->prepare($hist_sql_str);
	$sth->execute();
	my $data_refs = $sth->fetchall_arrayref;
	my $row_count = $sth->rows;
	### error checking ????? ##############
	
	foreach (@{$data_refs})			
	{
		next if not defined($_->[$title]); 
                next if $_->[$title] =~ /^\s*$/;

		if(exists($elimdups{$_->[$title]}))
		{
			$elimdups{$_->[$title]}->{url} = $_->[$url];	
			$elimdups{$_->[$title]}->{dateAdded} = $_->[$dateAdded];	
		}
		else
		{
			$elimdups{uc $_->[$title]} = { url => $_->[$url], 
					dateAdded => $_->[$dateAdded] };
		}		
	}	

	foreach (keys %elimdups)
	{
		#my @words = split /(?i:\s+)/i, $_, -1;
		my @words = split /(?:\s+)/, $_, -1;

		foreach (@words)
		{
			next if /(?:(\ba\b)|(\bas\b)|(\bthe\b)|(\bby\b)|(\bon\b)|(\band\b)|(\bis\b)|(\bFor\b)|(\bwith\b)|(\bIn\b)|(\bto\b)|(\bof\b)|(\b( +)\b)|(-|\+)|(\|)|[&-:><'#])/i;
			next if /\b[[:cntrl:]]+\b/;
			next if not /[\x00-\x7f]/;
			s/\s+$//g;
			s/^\s+//g;
			if (exists($markHist{$_}))
			{
				$markHist{$_}->{count}++;
			}
			else
			{
				$markHist{$_} = { count => 1 };
			}

		}

	}
      
       my @markHistHiLo = 
       sort { $b->[1] <=> $a->[1] } 
       map { [ $_, $markHist{$_}->{count} ] }
       keys %markHist;

      my $AT = 'A'; 
      my $nxt = 3;
      my $AL = '';
      my $FL = 0;
      my %H = ();

     for my $mrow (@markHistHiLo) {
     if(exists ($H{$mrow->[1] . $AL}) && ($FL == $nxt)) {
          $AL = $AT; 
          $AT++;
          $H{$mrow->[1] . $AL} = $mrow->[0];
          $FL = 0;
     }
        elsif (exists $H{$mrow->[1] . $AL} ) {
          $H{$mrow->[1] . $AL} .= "|" . $mrow->[0];
          $FL++;
     } 
       else { 
          $H{$mrow->[1]} =  $mrow->[0];
          $AL = '';
          $FL = 0;
     } 

   } #end for
  
   {
    no warnings;
   for my $k (sort { $b <=> $a}  keys %H) {
      my ($d) = ($k =~ /(\d+)/);
      push @H, $H{$k};
      printf("%-85s %-30s %2d\n", $H{$k}, '#' x $d, $d);
   }
#   print "$H[1],$H[2],$H[3],$H[4],$H[5],$H[6],$H[7],$H[8]\n";
#   print join "\n" ,@H[1..11];
   }

#   gen_optionlistForm();

}

sub gen_optionListDiv
{
   gen_histogram();
   my $str;
   for my $option (@H[1..15])
   {
       $option =~ s/\|/ /g; 
       $str .= qq#\n\t<option value="$option"> $option</option>#;
   }
   my $out_hist_opts = <<"OPTION_TABLE";
       <div style="display:inline-block" id="optionDiv">
       <form>
       <select  onchange="topOpToSearch(this.options[this.options.selectedIndex].text);" id="topOptionID" name="topOption">
          $str 
       </select>
       </form>
       </div>
OPTION_TABLE
   return $out_hist_opts; 
}


gen_histogram();

#gen_optionlistForm();
