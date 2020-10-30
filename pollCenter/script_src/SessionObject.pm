package SessionObject;

use strict;


sub new 
{
	my $class = shift;
	my $self = {};

	$self->{POLLCENTERID} = shift;
	$self->{QID} = shift;
	$self->{CAPTCHA} = shift;
	$self->{NULL1} = shift;
	$self->{NULL2} = shift;
	bless $self, $class;	
	return $self; 

}


1;
