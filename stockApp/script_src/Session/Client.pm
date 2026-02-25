package Session::Client;

use strict;
use lib "../../script_src"; # temporary use...will go away
use IPC::Shareable;
use Error;
#use LOGGER;
use Data::Dumper;

my $glue='sess';
my %default_options = (
     create    => 0,
     exclusive => 0,
     mode      => 0666,
     destroy   => 0, # !!!!!!!!!!!!!!!! changed from 0 to yes to test !!!!!!!!!!!!  #
     );			 # still testing IPC module. not very well documented..seems slower than it should be
			 # could be the old linux box.
my %sessionHash = ();

sub new
{
	my $class = shift; 
	my $sessionInstance = shift;
	my $self = \%sessionHash; 
	
	#%default_options = %{shift()} if defined(@_);	
		
	my $var = ();
	$var = tie %sessionHash, 'IPC::Shareable', $sessionInstance, { %default_options } or
     	die "client: tie failed\n";
	LOGGER::LOG("TIE ** $sessionInstance $var ** TIE");
		
	bless $self, $class;
	return $self;	

}

sub setSessionID
{
	my $self = shift;
	my $sessID = shift;
	my $userID = shift;

	$self->{$sessID} = ();

}

sub validateSessionID
{
	my $self = shift;
	my $sessID = shift;

	return $true if exists $self->{$sessID}; 
	return Error->new(106);

}

sub getSessionObject
{
        my $self = shift();
        my $sessionID = shift();
	#LOGGER::LOG("<<<<<<<<<<<< $sessionID >>>>>>>>>>>>>>>>>>>");
	#LOGGER::LOG("<<<<<<<<<<<< $self->{$sessionID} >>>>>>>>>>>>>>>>>>>");
	#LOGGER::LOG(Dumper($self->{$sessionID}));
        return Error->new(105) unless exists $self->{$sessionID}
                        and defined $self->{$sessionID};
        return $self->{$sessionID};

}

sub setSessionObject
{
	my $self = shift;
	die if scalar(@_) < 2;
	my $sessionID = shift;
	my $sessObj = shift;
	$self->{$sessionID} = $sessObj;

#	LOGGER::LOG("** setSessionObject **");
#	LOGGER::LOG(Dumper($self->{$sessionID}));
#	LOGGER::LOG("** setSessionObject **");

}

sub setQueryID
{
	my $self = shift;
	my ($sessID,$qID) = @_;
	
	return Error->new(106) unless defined $sessID and defined $qID;
	
	$self->{$sessID}->{queryID} = $qID;
}

sub getQueryID
{
        my $self = shift;
        my $sessID = shift;

        return Error->new(107) unless defined($self->{$sessID}->{queryID});
        return $self->{$sessID}->{queryID};

}


sub isset
{ return (defined($_[0]) && ($_[0] !~ /^\s*$/)); }


1;
