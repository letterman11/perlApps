package GenProfile;

@ISA = qw(GenView);

use strict;
use CGI;
use CGI::Carp;
use StockUtil;


sub new
{
	my $class = shift;
	my $self = {};
	my $profile_arr = shift;	

	$self->{PROFILE} = $profile_arr;
	bless ($self,$class);

}

sub display
{

	my $self = shift;
	my ($userName,$firstName,$lastName,
			$address1,$address2,$zipCode,$phone,
				$emailAddress,$state,$city) = (0..9);


	my $out_buffer = <<OUT_HTML;

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<HTML>
  <HEAD>
    <TITLE>Stock Query Application - Registration </TITLE>
        <LINK href="$::URL_PATHS->{MAINSTYLE_CSS}" rel="stylesheet" type="text/css">
        <script language="Javascript" src="$::URL_PATHS->{VALIDATION_JS}"> </script>
        <script language="Javascript" src="$::URL_PATHS->{COMMON_JS}"> </script>
	<script language="Javascript" type="text/javascript">	
	var userName 	= "$self->{PROFILE}->[$userName]";
	var firstName 	= "$self->{PROFILE}->[$firstName]";
	var lastName 	= "$self->{PROFILE}->[$lastName]";
	var address1 	= "$self->{PROFILE}->[$address1]";
	var address2 	= "$self->{PROFILE}->[$address2]";
	var zipCode 	= "$self->{PROFILE}->[$zipCode]";
	var phone 	= "$self->{PROFILE}->[$phone]";
	var emailAddress = "$self->{PROFILE}->[$emailAddress]";
	var state 	= "$self->{PROFILE}->[$state]";
	var city 	= "$self->{PROFILE}->[$city]";
	</script>
    </HEAD>
  <BODY onLoad="init_profile()">

OUT_HTML

	print $out_buffer;
	$self->display_header();
	print StockUtil::slurp_file($::URL_PATHS->{DIV_UPDATE_PROF_FHM});
	$self->display_footer();

	$out_buffer = <<"OUT_HTML";	
	
 </BODY>
 </HTML>

OUT_HTML

	print $out_buffer;

}







1;
