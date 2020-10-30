package globals;

use strict;

BEGIN
{
	require Exporter;
	our 		(@ISA, @EXPORT, @EXPORT_OK);
	@ISA 		= qw(Exporter);
	@EXPORT 	= qw();
	@EXPORT_OK 	= qw();

}
	
our %tabMap = ('tab_AE',1,'tab_FJ',2,'tab_KP',3,'tab_QU',4,'tab_VZ',5,'tab_SRCH_TITLE',6,'tab_SRCH_URL',7,'tab_SRCH_DATE',8,'tab_DATE',9,'searchBox',10);

our $true   = 1;
our $false  = 0;

my $config_file = "webMarks.cfg";
%globals::cfg = ();

### Do not enable no config file ##
###read_config();##################
###################################
sub read_config
{
	my $curr_sec;

	open(FH, "<$config_file") or die "Cannot open: $config_file\n";
	while(<FH>)
	{
		next if /^#+/;
		next if /^\s*$/;
		if (/\[(\S+)\]/)
		{
			$curr_sec = $1;
			$curr_sec = uc($curr_sec);
			$globals::cfg{$curr_sec} = {};
		}
		elsif (/=/)
		{
			my ($key,$value)= split /=/;
			$key =~ s/\s*//g;
			$value =~ s/\s*\t*//g;
			chomp($key,$value);
			$globals::cfg{$curr_sec}->{$key}=$value;
		}
	}
close(FH);
}

1;
