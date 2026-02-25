#!/usr/bin/perl -w

use strict;
use IPC::Shareable;


my $glue='sess';
my %default_options = (
     create    => 'yes',
     exclusive => 0,
     mode      => 0666,
     destroy   => 'yes',
     );

my %sessionHash = ();

my $shared_handle = tie %sessionHash, 'IPC::Shareable', $glue, { %default_options } or
die "client: tie failed\n";



#------- SIGNAL CATCHERS -----------------------------------#
$SIG{KILL} = \&catchkill;
sub catchkill
{
     $SIG{KILL} = \&catchkill;
	$shared_handle->clean_up_all;	
     print "######## CAUGHT KILL SIGNAL DYING #########\n";
     exit;
}
$SIG{TERM} = \&catchterm;
sub catchterm
{
     $SIG{TERM} = \&catchterm;
	$shared_handle->clean_up_all;	
     print "######## CAUGHT TERM SIGNAL SHUTTING DOWN #########\n";
     exit;
}



while (1) {
  sleep 15; # infinite server until handle of signal
  for my $key (keys %sessionHash) {
	print $key, "\n";

  }

}

