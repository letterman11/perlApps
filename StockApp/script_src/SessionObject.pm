package SessionObject;

use strict;


sub new 
{
	my $class = shift;
	my $self = {};

	$self->{INSTANCE} = shift;
	$self->{SESSIONID} = shift;
	$self->{DATA} = shift;
	$self->{ROWCOUNT} = shift;
	$self->{SORT} = shift;
	bless $self, $class;	
	return $self; 

}


1;
