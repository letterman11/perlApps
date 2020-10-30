package GenStatus;

use strict;
use Util;

sub new
{
	my $class = shift();
	my $self = {};
        bless ($self,$class);
	return $self;
}


sub display
{
   my $self = shift(); 
   my $errstr = shift if @_;
   
   my $out_buffer = ();

   print Util::headerHttp();
   $out_buffer = <<"OUT_HTML";

<div id="app_status">

	<span class="text_large"> <p> $errstr </p> </span>
</div>

OUT_HTML
   print $out_buffer;
   Util::footerHtml();
}











1;
