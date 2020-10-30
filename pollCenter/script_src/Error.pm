package Error;

use strict;

BEGIN
{
     require         Exporter;

     use vars          qw(@ISA @EXPORT @EXPORT_OK);
     @ISA            = qw(Exporter);
     @EXPORT         = qw($true $false);
     @EXPORT_OK      = qw();
}

my $true             = 1;
my $false            = 0;


my %err_codes = ( 
			101 => "Failed Login",
			102 => "Database Failure",
			103 => "Session Exists",
			104 => "No Session Exists for ID",
			105 => "No Object exists for Session",
			106 => undef,
			107 => undef,
			108 => undef,
			109 => undef,
			110 => undef,
			111 => undef,
			112 => undef,
			113 => undef,
			114 => undef,
			1062 => "User name or email address has already been taken",
			ERRCOND => undef,
		);	



sub new
{
	my $class = shift;
	my $code  = shift; 
	my $self = \%err_codes;
	$self->{ERRCOND} = $code;
	bless ($self, $class);
	return $self;   

}


sub errText
{
	my $self = shift;
	return $self->{$self->{ERRCOND}};
}





1;
