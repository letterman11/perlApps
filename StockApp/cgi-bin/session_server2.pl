#!/usr/bin/perl -w

use strict;
use IPC::Shareable;
require 'config.pl';

my %default_options = (
     create    => 'yes',
     exclusive => 0,
     mode      => 0666,
     destroy   => 'yes',
     );

my $i    = 0;


for my $instance (@{$::SESSION_CONFIG->{INSTANCES}}) {
   tie %{@{$::SESSION_CONFIG->{HASHES}}[$i++]}, 'IPC::Shareable', $instance, { %default_options } or
   die "client: tie failed\n";
} 


#------- SIGNAL CATCHERS -----------------------------------#
$SIG{KILL} = \&catchkill;
sub catchkill
{
     $SIG{KILL} = \&catchkill;
     print "######## CAUGHT KILL SIGNAL DYING #########\n";
     IPC::Shareable->clean_up_all;
     sleep 2;
     print "######## CAUGHT KILL SIGNAL SHUTTING DOWN #########\n";
     exit;
}

$SIG{TERM} = \&catchterm;
sub catchterm
{
     $SIG{TERM} = \&catchterm;
     print "######## CAUGHT TERM SIGNAL DYING #########\n";
     IPC::Shareable->clean_up_all;
     sleep 2; # delay apparently needed for IPC module to do full cleanup
     print "######## CAUGHT TERM SIGNAL SHUTTING DOWN #########\n";
     exit;
}

$SIG{INT} = \&catchint;
sub catchint
{
     $SIG{INT} = \&catchint;
     print "######## CAUGHT INT SIGNAL DYING #########\n";
     IPC::Shareable->clean_up_all;
     sleep 2; # delay apparently needed for IPC module to do full cleanup
     print "######## CAUGHT INT SIGNAL SHUTTING DOWN #########\n";
     exit;
}


while (1) {
  sleep 5; # infinite server until handle of signal
  for my $arr (@{$::SESSION_CONFIG->{HASHES}}) {
    for my $key (keys %{$arr}) {
      print $key, "\n";
  }

}

}

