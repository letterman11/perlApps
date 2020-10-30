package GenError;


use strict;
use Util;


sub new
{
        my $class = shift();
        my $self = {};
	$self->{ERROBJ} = shift if @_;
        bless ($self,$class);
	return $self;
}

sub display
{
   my $self = shift(); 
   my $errstr = shift if @_;
   my $out_buffer = ();
 
   $errstr = exists($self->{ERROBJ}) && $self->{ERROBJ}->errText ? $self->{ERROBJ}->errText : $errstr;


   print Util::headerHttp();
   $out_buffer = <<"OUT_HTML";
<div id="app_error">
	<span class="errtext_large"> <p> $errstr </p> </span>
</div>

</body>
</html>
OUT_HTML
   print $out_buffer;
   Util::footerHtml();
}










1;
