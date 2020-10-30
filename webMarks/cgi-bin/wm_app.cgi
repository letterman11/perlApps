#!/usr/bin/perl -wT

use strict;
use lib "/home/angus/dcoda_net/private/webMarks/script_src";
require '/home/angus/dcoda_net/cgi-bin/webMarks/cgi-bin/gen_histo_gram_multi.pl';
use globals;
use DbConfig;
use DBD::SQLite;
use CGI qw (:standard);
use Util;
use Error;
use GenMarks;

my $query = new CGI;

my $exec_sql_str;
my $executed_sql_str;
our $NO_HEADER = 0;

#alias app globals
my $DEBUG = $globals::true;
my %tabMap = %globals::tabMap;

########################  SQL STRINGS ####################################
my $main_sql_str = "select b.url, a.title, a.dateAdded from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID and a.USER_ID = ? and  (";
my $hist_sql_str = "select b.url, a.title, a.dateAdded from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID and a.USER_ID = ?  "; 
#my $date_sql_str = "select b.url, a.title, a.dateAdded from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID and a.USER_ID = ?  order by a.dateAdded desc limit 100";
my $date_sql_str = "select b.url, a.title, a.dateAdded from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID and a.USER_ID = ?  order by a.dateAdded ";


my $AE_str = " a.title like 'A%' or  a.title like 'a%' or  a.title like 'B%' or  a.title like 'b%' or  a.title like 'C%' or  a.title like 'c%' or  a.title like 'D%' or  a.title like 'd%'  or  a.title like 'E%' or  a.title like 'e%'";
my $FJ_str = " a.title like 'F%' or  a.title like 'f%'  or  a.title like 'G%' or  a.title like 'g%'  or  a.title like 'H%' or  a.title like 'h%'  or  a.title like 'I%' or  a.title like 'i%'  or  a.title like 'J%' or  a.title like 'j%'";
my $KP_str = " a.title like 'K%' or  a.title like 'k%'  or  a.title like 'L%' or  a.title like 'l%'  or  a.title like 'M%' or  a.title like 'm%'  or  a.title like 'N%' or  a.title like 'n%'  or  a.title like 'O%' or  a.title like 'o%'or  a.title like 'P%' or  a.title like 'p%'";
my $QU_str = " a.title like 'Q%' or  a.title like 'q%'  or  a.title like 'R%' or  a.title like 'r%'  or  a.title like 'S%' or  a.title like 's%'  or  a.title like 'T%' or  a.title like 't%'  or  a.title like 'U%' or  a.title like 'u%'";
my $VZ_str = " a.title like 'V%' or  a.title like 'v%'  or  a.title like 'W%' or  a.title like 'w%'  or  a.title like 'X%' or  a.title like 'x%'  or  a.title like 'Y%' or  a.title like 'y%'  or  a.title like 'Z%' or  a.title like 'z%'";

my $ORDER_BY_TITLE =  " ) order by a.title ";
my $ORDER_BY_DATE =  " ) order by a.dateAdded ";
########################  SQL STRINGS ####################################


my $dbconf = DbConfig->new();
#my $dbh = DBI->connect( "dbi:mysql:"
#my $dbh = DBI->connect( "dbi:SQLite:dbname="
#our $dbh = DBI->connect( "dbi:SQLite:dbname="
our $dbh = DBI->connect( "dbi:SQLite:dbname="
                . $dbconf->dbName() . ""
#                . $dbconf->dbName() . ":"
                . $dbconf->dbHost(),
                $dbconf->dbUser(),
                $dbconf->dbPass(), $::attr )
                or die "Cannot Connect to Database $DBI::errstr\n";


sub main_func
{
	my $wm_user_id;
	my $wm_user_name;
	my $q_parm = $query->url_param('req');

	if(defined($q_parm) && ($q_parm eq 'auth'))
	{
		my ($user_id,$user_name) = pre_auth();

		if(defined($user_id))
		{
			authorize($user_id,$user_name);		
		}
		else
		{
			GenMarks->new()->genDefaultPage( Error->new(112) );		
		}
	}
	elsif(defined($q_parm) && ($q_parm eq 'reg'))
	{
		GenMarks->new()->genRegistration();
	}
	elsif(defined($q_parm) && ($q_parm eq 'regAuth'))
	{
		my $callObj = formValidation($query);	
		
		if(ref $callObj eq 'Error')
		{

			GenMarks->new()->genRegistration($callObj);
		}
		else
		{

			my $sqlHash = $callObj;
			my $local_user_name = $sqlHash->{userName}; 
			my $partUserName = substr($sqlHash->{userName},0,5); 
			my $partID = substr(genSessionID(),0,5);
			my $userID = $partUserName."_".$partID;

			my $insert_sql_str = "INSERT INTO WM_USER (USER_ID,USER_NAME,USER_PASSWD,EMAIL_ADDRESS) VALUES (" . 
				"'$userID','$sqlHash->{userName}','$sqlHash->{password}','$sqlHash->{email}')";

			eval {
	
			my $sth = $dbh->prepare($insert_sql_str);
	
			$sth->execute();

			};

			if ($@) 
			{
				
				GenMarks->new()->genRegistration(Error->new(120));
			}
			else
			{
				GenMarks->new()->genDefaultPage("Registration Successful: $local_user_name");		
				
			}
		}
	}
	elsif(defined($wm_user_id = validateSession($query)->{wmUSERID})) 
	#elsif(defined($wm_user_id = validateSessionDB($query)->{wmUSERID})) 
	{
		#Continue in validated session
		$wm_user_name =  validateSession($query)->{wmUSERNAME};
		#$wm_user_name =  validateSessionDB($query)->{wmUSERNAME};

		if(defined($q_parm) && ($q_parm eq 'search'))
		{
			exec_page($wm_user_id,$wm_user_name);
		}
		elsif(defined($q_parm) && ($q_parm eq 'newMark'))
		{
			my $callObj = insert_mark($wm_user_id);
			exec_page($wm_user_id,$wm_user_name,$callObj);
		}
		elsif(defined($q_parm) && ($q_parm eq 'deltaPass'))
		{
			if(not mod_passwd())
			{
				GenMarks->new()->genDefaultPage();
			}
			else
			{
				exec_page($wm_user_id,$wm_user_name);
			}
		}	
		else
		{

			exec_page($wm_user_id,$wm_user_name);
		}
	}
	else
	{
		GenMarks->new()->genDefaultPage();
	}

}

sub exec_page
{

	my $user_id = shift;
	my $user_name = shift;
	my $errObj = shift;
	#my $NO_HEADER = 0;
	my $tabtype = $query->param('tab') || $tabMap{tab_DATE};
	my $qtext = $query->param('searchbox');
	my $qBool = $query->param('searchtype');
#	my $sort_crit = $query->param('sortCrit')||1;
	my $sort_crit = isset($query->param('sortCrit')) ? $query->param('sortCrit') : 1 ;
#	my $sort_crit = $query->param('sortCrit');
	my $qqtext = $query->param('searchbox2');
	my $ORDER_BY_CRIT;	
	my $sort_asc = 0;
	my $sort_desc = 1;
	my $sort_date_asc = 2;
	my $sort_date_desc = 3;
	my $storedSQLStr;
	my $sort_ord;	
	
	## Correct later
	if(ref $errObj ne 'Error') 
	{
		$NO_HEADER = $errObj;	
		$errObj = undef;
	}

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
#=cut
    if(($qBool eq "COMBO") && (isset($qtext)) && (isset($qqtext)))
    {
	     my $qstr;
            $qstr = " a.title like '%$qtext%'  and b.url like '%$qqtext%' ";# $sort_ord;


        $exec_sql_str = $main_sql_str . $qstr  . $ORDER_BY_DATE .  ' desc ' ;#$sort_ord;
        $storedSQLStr = $main_sql_str . $qstr ;
        storeSQL($storedSQLStr);
        $tabtype = $tabMap{tab_SRCH_TITLE};

    }
#=cut
    #if(defined($qtext) && ($qtext !~ /^\s*$/g))
    elsif(isset($qtext))
    #if(isset($qtext))
    {
           #$ORDER_BY_CRIT ;
        my @queri = split /\s+/, $qtext, -1;
        my $qstr;
        if (@queri < 2) 
        {
            $qstr = " a.title like '%$qtext%' ";# $sort_ord;
            $exec_sql_str = $main_sql_str . $qstr . $ORDER_BY_DATE  .' desc '  ;# $sort_ord;
               #$exec_sql_str = $main_sql_str . " a.title like '%$qtext%' " . $ORDER_BY_CRIT . $sort_ord;
        } 
        else 
        {
            $qstr = " a.title like '%$queri[0]%' ";
            for (my $i = 1; $i <= $#queri; $i++) 
            {
                if($qBool eq "AND") 
                {  
                    $qstr .= " and a.title like '%$queri[$i]%' " ;
                }
                else   
                { 
                 $qstr .= " or a.title like '%$queri[$i]%' " ;
                }
            }
            $exec_sql_str = $main_sql_str . $qstr  . $ORDER_BY_DATE .  ' desc ' ;#$sort_ord;
        }

        $storedSQLStr = $main_sql_str . $qstr ;
        storeSQL($storedSQLStr);
        $tabtype = $tabMap{tab_SRCH_TITLE};

        }
      #elsif(defined($qqtext) && ($qqtext !~ /^\s*$/g))
      elsif(isset($qqtext))
      {

	my $qstr;
        $qstr = " b.url like '%$qqtext%' ";# $sort_ord;
        $exec_sql_str = $main_sql_str . $qstr . $ORDER_BY_DATE  .' desc '  ;# $sort_ord;

        $storedSQLStr = $main_sql_str . $qstr ;
        storeSQL($storedSQLStr);
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
	    elsif($tabtype eq $tabMap{tab_DATE})
	    {
	      $date_sql_str .= $sort_ord . " limit 200 ";
	      $exec_sql_str = $date_sql_str;
	    }
	    elsif($tabtype eq $tabMap{tab_SRCH_TITLE})
        {
           $storedSQLStr = getStoredSQL();
	       $exec_sql_str = $storedSQLStr . $ORDER_BY_CRIT . $sort_ord;
        }
    }

    my $executed_sql_str = ($tabtype ne $tabMap{tab_DATE}) ? $exec_sql_str : $date_sql_str;

	print STDERR $executed_sql_str, "\n" if($DEBUG);

    my ($sth,$row_count,$data_refs,$genMarks);

    eval {
    $sth = $dbh->prepare($executed_sql_str);
    $sth->bind_param(1,$user_id);
    $sth->execute();
    };

	%tabMap = reverse %tabMap;

    if ($@) 
    {
	   $genMarks = GenMarks->new($tabMap{tabtype},undef,undef,Error->new(2000));	
	   $genMarks->genPage($user_name,$sort_crit,\%tabMap);
    }
	else
	{
	   $data_refs = $sth->fetchall_arrayref;
	   $row_count = $sth->rows;
	
	   $genMarks = GenMarks->new($tabMap{$tabtype},$data_refs,$row_count,$errObj);
	   $genMarks->genPage($user_name,$sort_crit,\%tabMap);
    }
}

sub insert_mark
{

	my $user_id = shift;
	my $title = $query->param('mark_title');
	my $url = $query->param('mark_url');

	return Error->new(151) if ((not isset($title)) || (not isset($url)));

	my $unix_epochs = time;	
	#use antique mozilla time format (1000 * 1000) unix epoch seconds => microseconds 
	my $dateAdded = $unix_epochs * (1000 * 1000);

	my $dbconf = DbConfig->new();
	#my $local_dbh = DBI->connect( "dbi:mysql:"
	my $local_dbh = DBI->connect( "dbi:SQLite:dbname="
                #. $dbconf->dbName() . ":"
                . $dbconf->dbName() . ""
                . $dbconf->dbHost(),
                $dbconf->dbUser(),
                $dbconf->dbPass(), $::attr2 )
                or die "Cannot Connect to Database $DBI::errstr\n";

	my ($tbl1MaxId) = $dbh->selectrow_array("select max(BOOKMARK_ID) from WM_BOOKMARK");
	my ($tbl2MaxId) = $dbh->selectrow_array("select max(PLACE_ID) from WM_PLACE");

	$tbl1MaxId++;
	$tbl2MaxId++;


	my ($dup_wm_place_url) = $local_dbh->selectrow_array("select b.url from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID and a.USER_ID = '$user_id' and b.URL = " . $local_dbh->quote($url) );

	return Error->new(150) if (defined($dup_wm_place_url));

	my $rc = $local_dbh->do("insert into WM_PLACE (PLACE_ID, URL, TITLE) values ($tbl2MaxId," . $local_dbh->quote($url) . ", " . $local_dbh->quote($title) . ")" );

	print STDERR "RCODE1 => $rc\n" if($DEBUG);

	if(not defined($rc)) {
		print STDERR "Failed DB Operation: $DBI::errstr\n" if($DEBUG);
		$local_dbh->disconnect;
		return Error->new(150);
	}

	my $rc2 = $local_dbh->do("insert into WM_BOOKMARK (BOOKMARK_ID, USER_ID, PLACE_ID, TITLE, DATEADDED) values ($tbl1MaxId, '$user_id', $tbl2MaxId," . $local_dbh->quote($title) . ", '$dateAdded' ) " );

	print STDERR "RCODE2 => $rc2\n" if($DEBUG);

	if(not defined($rc2)) {
		print STDERR "Failed DB Operation: $DBI::errstr\n" if($DEBUG);
		$local_dbh->disconnect;
		return Error->new(150);
	}

}

sub authorize
{
	my $host = undef;
	my $user_id = shift;
	my $user_name = shift;
	my $sessionID = genSessionID();
	my $init_count = 0;
	my $init_date_count = 0;
	my $init_tab_state = 0;

	my $c1 = new CGI::Cookie(-name=>'wmSessionID',
			-value=>$sessionID,
			-expires=>undef, 
			-domain=>$host,  
			-path=>'/');

	my $c2 = new CGI::Cookie(-name=>'wmUserID',
			-value=>$user_id,
			-expires=>undef, 
			-domain=>$host, 
			-path=>'/');

	my $c3 = new CGI::Cookie(-name=>'wmUserName',
			-value=>$user_name,
			-expires=>undef, 
			-domain=>$host, 
			-path=>'/');

	my $c4 = new CGI::Cookie(-name=>'Counter',
			-value=>$init_count,
			-expires=>undef, 
			-domain=>$host, 
			-path=>'/');

	my $c5 = new CGI::Cookie(-name=>'tab_state',
			-value=>$init_tab_state,
			-expires=>undef, 
			-domain=>$host, 
			-path=>'/');

	my $c6 = new CGI::Cookie(-name=>'dt_cnter',
			-value=>$init_date_count,
			-expires=>undef, 
			-domain=>$host, 
			-path=>'/');


	my $sessionInstance = 'sess1';

#	storeSessionDB($sessionInstance,
	storeSession($sessionInstance,
				$sessionID, 
				$user_id,
				$user_name);

	#---- CGI header response ----#
#
#
#
	print $query->header(-status=>200,
			     -cookie=>[$c1,$c2,$c3,$c4,$c5,$c6]
			    );
        $NO_HEADER = 1;
	exec_page($user_id,$user_name,$NO_HEADER);	
}

sub mod_passwd
{
	my ($usr_id,$usr_name,$usr_pass) = pre_auth();

	if(not defined($usr_name))
	{
		return 0;	
	}
	else
	{
		my $rc = $dbh->do("update WM_USER set user_passwd='" . $usr_pass . "'  where user_name='" . $usr_name . "' ");
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
		$exec_sql_str = "select user_id, user_name from WM_USER where user_passwd = '" . $old_usr_pass . "' and user_name ='" . $usr_name . "' ";
	} else {
		$exec_sql_str = "select user_id, user_name from WM_USER where user_passwd = '" . $usr_pass . "' and user_name ='" . $usr_name . "' ";
	}

	### error checking ????? ##############
	my $sth = $dbh->prepare($exec_sql_str);
	$sth->execute();
	my @user_row = $sth->fetchrow_array;
	my $row_count = $sth->rows;
	### error checking ????? ##############
	print STDERR  $$, "###### ", $user_row[1], " BOOOO #########\n" if($DEBUG);
	return ($user_row[0],$user_row[1],$usr_pass);
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
main_func();

#gen_histogram();


$dbh->disconnect() or print STDERR "Disconnection failed: $DBI::errstr\n" and warn "Disconnection failed: $DBI::errstr\n";

exit;
#:set tabstop=8 softtabstop=8
