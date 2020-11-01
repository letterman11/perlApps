#!/usr/bin/perl
use feature 'say';
use strict;
#romans 8:14-16

my $file = $ARGV[0] || "convert_calls.txt";

#"NAICS","Industry","# of Calls");
my (@line,$icode,$itext,$calls);
my $totCalls=0;
#say $file;

my %converts = {};
my @converts = ();

open(FH, $file) or die "Cannot open file $!";

#printf("%5s%55s%5s\n","NAICS","Industry","# of Calls");
while (<FH>) {
       my $line = $_;
       chomp($line);

	   next if /^\s*$/;

       ($icode,$itext,$calls) =  /^(\d+)\s+([\w\s\.\&\-\(\)\;,]+?)\s+(\d+)/;
	   $totCalls += $calls;

       push @converts , [ $icode, $itext, $calls ];
       ($icode,$itext,$calls) = /\d+\s+(\d+)\s+([\w\s\.\&\-\(\)\;,]+?)\s+(\d+)$/;
       next if $calls < 1; 
       $totCalls +=  $calls;
       push @converts , [ $icode, $itext, $calls ];
}


my @new_list = sort { $a->[2] <=> $b->[2]} @converts;

for my $line (@new_list) {

#   printf("%45s|%-25s %3d\n", @$line[1], "#" x @$line[2], @$line[2]);
   printf("%2d%45s|%-25s %3d\n", @$line[0], @$line[1], "#" x @$line[2], @$line[2]);

}

say "Totals:  $totCalls";
