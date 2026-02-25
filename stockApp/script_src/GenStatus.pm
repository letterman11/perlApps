package GenStatus;

use strict;
use StockUtil;

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

   print StockUtil::headerHtml();
   $out_buffer = <<"OUT_HTML";
<div id="header">
        <div id="banner">
	<a href="$::URL_PATHS->{STOCKAPP_HTM}"> <img id="banner_image" src="$::URL_PATHS->{BANNER_IMAGE}"> </a>
	<a href="$::URL_PATHS->{STOCKAPP_HTM}"> <img id="banner_image2" src="$::URL_PATHS->{BANNER_IMAGE2}"> </a>
        </div>
</div>

<div id="app_status">
	<br>
	<span class="text_large"> <p> $errstr </p> </span>
</div>

OUT_HTML
   print $out_buffer;
   StockUtil::footerHtml();
}











1;
