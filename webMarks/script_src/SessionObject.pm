package SessionObject;

use strict;


sub new 
{
	my $class = shift;
	my $self = {};

	$self->{INSTANCE} = shift;
	$self->{SESSIONID} = shift;
	$self->{USERID} = shift;
	$self->{USERNAME} = shift;
	$self->{DATA} = shift if @_;
	$self->{ROWCOUNT} = shift if @_;
	$self->{SORT} = shift if @_;
	bless $self, $class;	
	return $self; 

}


1;
