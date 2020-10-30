package DbConfig;

use strict;
use FileHandle;

$::attr = { 
		PrintError => 0,
		RaiseError => 1,
	}; 

sub new
{
	my $class = shift;
	my %configHash = ();
	my $self = \%configHash;

	my $defaultConfFile = "stockDbConfig.dat";

 	my $fh = new FileHandle;
	if ($fh->open("< $defaultConfFile") ) {
		while (<$fh>) {
			next if not /^([A-Za-z0-9]+)=([A-Za-z0-9\.]*)/; 
			my ($key,$value) = ($1,$2);
			$configHash{$key}=$value;
		} 
		$fh->close;
  	} else { die "Error opening configfile \n"; }

	bless ($self,$class);
	return $self; 
}


sub dbName 
{
	my $self = shift;
	return $self->{'database'};
}     
     
sub dbHost
{
	my $self = shift;
	return $self->{'hostname'};
}

sub dbUser
{
	my $self = shift;
	return $self->{'user'};
} 

sub dbPass
{
	my $self = shift;
	return $self->{'password'};
} 

sub rowsPerPage
{
	my $self = shift;
	return $self->{'rowsperpage'};

}   











1; 
