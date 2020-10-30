#!/usr/bin/perl -wT

use strict;
use lib "/home/abrooks/www/webMarks/script_src";
use globals;
use File::Copy;
use DBD::SQLite;
use CGI qw (:standard);
use GenMarks;

my $query = new CGI;

my %tabMap = ('tab_AE',0,'tab_FJ',1,'tab_KP',2,'tab_QU',3,'tab_VZ',4,'tab_SRCH_TITLE',5,'tab_SRCH_URL',6,'tab_SRCH_DATE',7,'tab_DATE',8,'searchBox',9);
my $exec_sql_str;

########################  SQL STRINGS ####################################
my $main_sql_str = "select b.url, a.title, a.dateAdded from moz_bookmarks a, moz_places b where a.fk = b.id  and (";
my $date_sql_str = "select b.url, a.title, a.dateAdded from moz_bookmarks a, moz_places b where a.fk = b.id  order by a.dateAdded desc limit 100";

my $AE_str = " a.title like 'A%' or  a.title like 'a%' or  a.title like 'B%' or  a.title like 'b%' or  a.title like 'C%' or  a.title like 'c%' or  a.title like 'D%' or  a.title like 'd%'  or  a.title like 'E%' or  a.title like 'e%'";
my $FJ_str = " a.title like 'F%' or  a.title like 'f%'  or  a.title like 'G%' or  a.title like 'g%'  or  a.title like 'H%' or  a.title like 'h%'  or  a.title like 'I%' or  a.title like 'i%'  or  a.title like 'J%' or  a.title like 'j%'";
my $KP_str = " a.title like 'K%' or  a.title like 'k%'  or  a.title like 'L%' or  a.title like 'l%'  or  a.title like 'M%' or  a.title like 'm%'  or  a.title like 'N%' or  a.title like 'n%'  or  a.title like 'O%' or  a.title like 'o%'or  a.title like 'P%' or  a.title like 'p%'";
my $QU_str = " a.title like 'Q%' or  a.title like 'q%'  or  a.title like 'R%' or  a.title like 'r%'  or  a.title like 'S%' or  a.title like 's%'  or  a.title like 'T%' or  a.title like 't%'  or  a.title like 'U%' or  a.title like 'u%'";
my $VZ_str = " a.title like 'V%' or  a.title like 'v%'  or  a.title like 'W%' or  a.title like 'w%'  or  a.title like 'X%' or  a.title like 'x%'  or  a.title like 'Y%' or  a.title like 'y%'  or  a.title like 'Z%' or  a.title like 'z%'";

my $ORDER_BY_TITLE =  " ) order by a.title ";
########################  SQL STRINGS ####################################

#my $bmDB = $bkcfg{BOOKMAN}->{bmDB};

#print STDERR $bmDB, "\n";

#copy($bmDB,"/tmp/places.sqlite.tmp.DB") or die "Error Cannot copy $!\n";

my $dbh = DBI->connect("dbi:SQLite:dbname=places.sqlite","","") or die "Error $!\n";

my $tabtype = $query->param('tab') || 0;
my $qtext = $query->param('searchbox');
my $qtext2 = $query->param('searchbox2');

if((defined($qtext) && ($qtext !~ /^\s*$/g)) && (defined($qtext2) && ($qtext2 !~ /^\s*$/g)))
{
   $exec_sql_str = $main_sql_str . " a.title like '%$qtext%' or a.title like '%$qtext2%' " . $ORDER_BY_TITLE;
   $tabtype = $tabMap{tab_SRCH_TITLE};
}
elsif(defined($qtext) && ($qtext !~ /^\s*$/g))
{
   $exec_sql_str = $main_sql_str . " a.title like '%$qtext%'" . $ORDER_BY_TITLE;
   $tabtype = $tabMap{tab_SRCH_TITLE};
}
else
{
   if($tabtype eq $tabMap{tab_AE}) 
   {
      $exec_sql_str = $main_sql_str . $AE_str . $ORDER_BY_TITLE;
   }
   elsif($tabtype eq $tabMap{tab_FJ})
   {
      $exec_sql_str = $main_sql_str . $FJ_str . $ORDER_BY_TITLE;
   }
   elsif($tabtype eq $tabMap{tab_KP})
   {
      $exec_sql_str = $main_sql_str . $KP_str . $ORDER_BY_TITLE;
   }
   elsif($tabtype eq $tabMap{tab_QU})
   {
      $exec_sql_str = $main_sql_str . $QU_str . $ORDER_BY_TITLE;
   }
   elsif($tabtype eq $tabMap{tab_VZ})
   {
      $exec_sql_str = $main_sql_str . $VZ_str . $ORDER_BY_TITLE;
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

print header;
$genMarks->genPage();

exit;

