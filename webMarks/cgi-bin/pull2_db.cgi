#!/usr/bin/perl -wT

use strict;
use lib "/Users/tcguest02/tools/projects/webMarks/script_src";
use globals;
use File::Copy;
use DBD::SQLite;
use CGI qw (:standard);
use Util;
use GenMarks;

my $query = new CGI;

my %tabMap = ('tab_AE',0,'tab_FJ',1,'tab_KP',2,'tab_QU',3,'tab_VZ',4,'tab_SRCH_TITLE',5,'tab_SRCH_URL',6,'tab_SRCH_DATE',7,'tab_DATE',8,'searchBox',9);
my $exec_sql_str;
my $executed_sql_str;

########################  SQL STRINGS ####################################
my $main_sql_str = "select b.url, a.title, a.dateAdded from moz_bookmarks a, moz_places b where a.fk = b.id  and (";
my $hist_sql_str = "select b.url, a.title, a.dateAdded from moz_bookmarks a, moz_places b where a.fk = b.id "; 
my $date_sql_str = "select b.url, a.title, a.dateAdded from moz_bookmarks a, moz_places b where a.fk = b.id  order by a.dateAdded desc limit 100";

#my $insert_sql_str1 = "insert into moz_bookmarks values ( ) ";
#my $insert_sql_str2 = "insert into moz_places values ( ) ";

my $AE_str = " a.title like 'A%' or  a.title like 'a%' or  a.title like 'B%' or  a.title like 'b%' or  a.title like 'C%' or  a.title like 'c%' or  a.title like 'D%' or  a.title like 'd%'  or  a.title like 'E%' or  a.title like 'e%'";
my $FJ_str = " a.title like 'F%' or  a.title like 'f%'  or  a.title like 'G%' or  a.title like 'g%'  or  a.title like 'H%' or  a.title like 'h%'  or  a.title like 'I%' or  a.title like 'i%'  or  a.title like 'J%' or  a.title like 'j%'";
my $KP_str = " a.title like 'K%' or  a.title like 'k%'  or  a.title like 'L%' or  a.title like 'l%'  or  a.title like 'M%' or  a.title like 'm%'  or  a.title like 'N%' or  a.title like 'n%'  or  a.title like 'O%' or  a.title like 'o%'or  a.title like 'P%' or  a.title like 'p%'";
my $QU_str = " a.title like 'Q%' or  a.title like 'q%'  or  a.title like 'R%' or  a.title like 'r%'  or  a.title like 'S%' or  a.title like 's%'  or  a.title like 'T%' or  a.title like 't%'  or  a.title like 'U%' or  a.title like 'u%'";
my $VZ_str = " a.title like 'V%' or  a.title like 'v%'  or  a.title like 'W%' or  a.title like 'w%'  or  a.title like 'X%' or  a.title like 'x%'  or  a.title like 'Y%' or  a.title like 'y%'  or  a.title like 'Z%' or  a.title like 'z%'";

my $ORDER_BY_TITLE =  " ) order by a.title ";
my $ORDER_BY_DATE =  " ) order by a.dateAdded ";
########################  SQL STRINGS ####################################

#my $bmDB = $bkcfg{BOOKMAN}->{bmDB};

#print STDERR $bmDB, "\n";


my $dbh = DBI->connect("dbi:SQLite:dbname=places.sqlite","","") or die "Error $!\n";


sub validate
{
	if($query->url_param('req') eq 'auth')
	{
		my ($user_id) = pre_auth();

		if(defined($user_id))
		{
			authorize($user_id);		
		}
		else
		{
			print header;
			GenMarks->new()->genDefaultPage();		
		}
	}
	elsif(ref(Util::validateSession($query)) eq 'SessionObject') 
	{
		#Do some stuff
		if($query->url_param('req') eq 'newMark')
		{
			insert_mark();
			exec_page();
		}
		elsif($query->url_param('req') eq 'deltaPass')
		{
			if(not mod_passwd())
			{
				print header;
				GenMarks->new()->genDefaultPage();
			}
			else
			{
				exec_page();
			}
		}	
		else
		{

			exec_page();
		}
	}
	else
	{
		print header;
		GenMarks->new()->genDefaultPage();
	}

}

sub exec_page
{

	my $user_id = shift;
	my $tabtype = $query->param('tab') || 0;
	my $qtext = $query->param('searchbox');
	my $sort_crit = $query->param('sortCrit');
	my $qtext2 = ();
	my $ORDER_BY_CRIT;	
	my $sort_asc = 0;
	my $sort_desc = 1;
	my $sort_date_asc = 2;
	my $sort_date_desc = 3;
	my $sort_ord;	

	if($sort_crit == 0)
	{
		$ORDER_BY_CRIT = $ORDER_BY_TITLE;
		$sort_ord = ' asc ';	
	}
	elsif($sort_crit == 1)
	{
		$ORDER_BY_CRIT = $ORDER_BY_TITLE;
		$sort_ord = ' desc ';
	}
	elsif($sort_crit == 2)
	{
		$ORDER_BY_CRIT = $ORDER_BY_DATE;
		$sort_ord = ' asc ';
	}
	else
	{
		$ORDER_BY_CRIT = $ORDER_BY_DATE;
		$sort_ord = ' desc ';
	}


	if((defined($qtext) && ($qtext !~ /^\s*$/g)) && (defined($qtext2) && ($qtext2 !~ /^\s*$/g)))
	{
	   $exec_sql_str = $main_sql_str . " a.title like '%$qtext%' or a.title like '%$qtext2%' " . $ORDER_BY_TITLE;
	   $tabtype = $tabMap{tab_SRCH_TITLE};
	}
	elsif(defined($qtext) && ($qtext !~ /^\s*$/g))
	{
	   $exec_sql_str = $main_sql_str . " a.title like '%$qtext%' " . $ORDER_BY_TITLE . $sort_ord;
 
	   $tabtype = $tabMap{tab_SRCH_TITLE};
	}
	else
	{
	   if($tabtype eq $tabMap{tab_AE}) 
	   {
	      $exec_sql_str = $main_sql_str . $AE_str . $ORDER_BY_CRIT . $sort_ord;
	   }
	   elsif($tabtype eq $tabMap{tab_FJ})
	   {
	      $exec_sql_str = $main_sql_str . $FJ_str . $ORDER_BY_CRIT . $sort_ord;
	   }
	   elsif($tabtype eq $tabMap{tab_KP})
	   {
	      $exec_sql_str = $main_sql_str . $KP_str . $ORDER_BY_CRIT . $sort_ord;
	   }
	   elsif($tabtype eq $tabMap{tab_QU})
	   {
	      $exec_sql_str = $main_sql_str . $QU_str . $ORDER_BY_CRIT . $sort_ord;
	   }
	   elsif($tabtype eq $tabMap{tab_VZ})
	   {
	      $exec_sql_str = $main_sql_str . $VZ_str . $ORDER_BY_CRIT . $sort_ord;
	   }
	
	}

	my $executed_sql_str = ($tabtype ne $tabMap{tab_DATE}) ? $exec_sql_str : $date_sql_str;

	print STDERR $executed_sql_str, "\n";

	### error checking ????? ##############
	my $sth = $dbh->prepare($executed_sql_str);
	$sth->execute();
	my $data_refs = $sth->fetchall_arrayref;
	my $row_count = $sth->rows;
	### error checking ????? ##############
	
	%tabMap = reverse %tabMap;
	my $genMarks = GenMarks->new($tabMap{$tabtype},$data_refs,$row_count);
	
	print header if not defined $user_id;
	$genMarks->genPage();
}

sub insert_mark
{

	my $title = $query->param('mark_title');
	my $url = $query->param('mark_url');

	my $unix_epochs = time;	
	#use antique mozilla time format (1000 * 1000) unix epoch seconds => microseconds 
	my $dateAdded = $unix_epochs * (1000 * 1000);

	my ($tbl1MaxId) = $dbh->selectrow_array("select max(id) from moz_bookmarks");
	my ($tbl2MaxId) = $dbh->selectrow_array("select max(id) from moz_places");

	$tbl1MaxId++;
	$tbl2MaxId++;

	my $typeID = 1; # needed for moz_bookmarks
	my $parentID = 5; # needed for moz_bookmarks_roots


	my $rc = $dbh->do("insert into moz_bookmarks (id, fk, title, dateAdded, type, parent) values ($tbl1MaxId, $tbl2MaxId," . $dbh->quote($title) . ",'$dateAdded',$typeID,$parentID)");

	print STDERR "RCODE1 => $rc\n";

	if(not defined($rc)) {
		print STDERR "Failed DB Operation: $DBI::errstr\n";
		return 0;
	}

	my $rc2 = $dbh->do("insert into moz_places (id, url, title) values ($tbl2MaxId," . $dbh->quote($url) . ", " . $dbh->quote($title) . ")");

	print STDERR "RCODE2 => $rc2\n";

	if(not defined($rc2)) {
		print STDERR "Failed DB Operation: $DBI::errstr\n";
		return 0;
	}

	return 1;

}

sub authorize
{
	my $host = undef;
	my $user_id = shift;
	my $sessionID = Util::genSessionID();
	my $init_count = 0;
	my $init_date_count = 0;
	my $init_tab_state = 0;

	my $c1 = new CGI::Cookie(-name=>'SessionID',
			-value=>$sessionID,
			-expires=>undef, 
			-domain=>$host,  
			-path=>'/');

	my $c2 = new CGI::Cookie(-name=>'UserID',
			-value=>$user_id,
			-expires=>undef, 
			-domain=>$host, 
			-path=>'/');

	my $c3 = new CGI::Cookie(-name=>'Counter',
			-value=>$init_count,
			-expires=>undef, 
			-domain=>$host, 
			-path=>'/');

	my $c4 = new CGI::Cookie(-name=>'tab_state',
			-value=>$init_tab_state,
			-expires=>undef, 
			-domain=>$host, 
			-path=>'/');

	my $c5 = new CGI::Cookie(-name=>'dt_cnter',
			-value=>$init_date_count,
			-expires=>undef, 
			-domain=>$host, 
			-path=>'/');

	my $sessionInstance = 'sess1';

	Util::storeSession($sessionInstance,
				$sessionID, 
				$user_id);

	#---- CGI header response ----#
	print $query->header(-status=>200,
			     -cookie=>[$c1,$c2,$c3,$c4,$c5]
			    );

	exec_page($user_id);	
}

sub mod_passwd
{
	my ($usr_id,$usr_pass) = pre_auth();

	if(not defined($usr_id))
	{
		return 0;	
	}
	else
	{
		my $rc = $dbh->do("update user set user_pass='" . $usr_pass . "'  where user_id='" . $usr_id . "' ");
		if(not defined($rc))
		{
			return 0;
		}
		else
		{
			return 1;			
		}
	}
}

sub pre_auth
{
	my $usr_name = $query->param('user_name');
	my $usr_pass = $query->param('user_pass'); 
	my $old_usr_pass = $query->param('old_pass'); #only for update
	my $exec_sql_str;
	
	if(defined($old_usr_pass)) {
		$exec_sql_str = "select user_id from user where user_pass = '" . $old_usr_pass . "' and user_id ='" . $usr_name . "' ";
	} else {
		$exec_sql_str = "select user_id from user where user_pass = '" . $usr_pass . "' and user_id ='" . $usr_name . "' ";
	}

	### error checking ????? ##############
	my $sth = $dbh->prepare($exec_sql_str);
	$sth->execute();
	my @user_row = $sth->fetchrow_array;
	my $row_count = $sth->rows;
	### error checking ????? ##############
	return ($user_row[0],$usr_pass);
}

sub gen_histogram
{
	my %markHist = ();
	my %elimdups = ();
	my @histo_list = ();	
	my ($title,$url,$dateAdded) = (1,0,2);

	### error checking ????? ##############
	my $sth = $dbh->prepare($hist_sql_str);
	$sth->execute();
	my $data_refs = $sth->fetchall_arrayref;
	my $row_count = $sth->rows;
	### error checking ????? ##############
	
	foreach (@{$data_refs})			
	{
		next if not defined($_->[$title]);
		if(exists($elimdups{$_->[$title]}))
		{
			$elimdups{$_->[$title]}->{url} = $_->[$url];	
			$elimdups{$_->[$title]}->{dateAdded} = $_->[$dateAdded];	
		}
		else
		{
			$elimdups{$_->[$title]} = { url => $_->[$url], 
					dateAdded => $_->[$dateAdded] };
		}		
	}	

	foreach (keys %elimdups)
	{
		my @words = split /(?:\s+)/, $_, -1;

		foreach (@words)
		{
			next if /(?:[A|a]|(The)|(the)|(And)|(and)|(For)|(for)|(In)|(in)|(To)|(to)|[Oo]f|\s+|\t+|(-)+|[0-9\&\-\:\>\<\'\#])/;
			s/\s+$//g;
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

	#map { printf("KeyWord => *%-15s* \tCount => %s\n", $_, $markHist{$_}->{count}); } sort { $markHist{$b}->{count} <=> $markHist{$a}->{count} } keys %markHist;
	gen_json(\%elimdups);
}

sub gen_json
{	
	my %in_hash = %{ shift() };
	my $json_out;
	my $json_out_;
	
	foreach (keys %in_hash)
	{
		$json_out_ .= " { \"title\" : \"$_\", \"url\" : \"$in_hash{$_}->{url}\", \"dateAdded\" : $in_hash{$_}->{dateAdded} },\n ";
	}

	$json_out = sprintf("{\n %s \n}",$json_out_);
	print $json_out, "\n";

}

#=============================== MAIN =====================================
#validate();

gen_histogram();


$dbh->disconnect() or print STDERR "Disconnection failed: $DBI::errstr\n" and warn "Disconnection failed: $DBI::errstr\n";

exit;

