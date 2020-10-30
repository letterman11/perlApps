package GenLogin;

@ISA = qw(GenView);

use strict;
use StockUtil;



sub stockHeaderHtml
{
  print "\n<tr><th> GenLogin TA NUMBER </th><th> STOCK SYMBOL</th><th> LIMIT PRICE </th><th> ORDER QUANTITY </th> </tr>\n";

}


sub display
{
   my $self = shift(); 
   my $errstr = shift if @_;
   
   my $out_buffer = ();

   print StockUtil::headerHtml();
   $out_buffer = <<"OUT_HTML";
<div id="main">
        <div id="banner">
  	 <a  href="$::URL_PATHS->{STOCKAPP_HTM}">   <img id="banner_image" src="$::URL_PATHS->{BANNER_IMAGE}">  </a>
  	 <a  href="$::URL_PATHS->{NEWSITE_HTM}">   <img id="banner_image2" src="$::URL_PATHS->{BANNER_IMAGE2}">  </a>
        </div>

        <div id="login" style="visibility:visible">
          <form name="frmLogin" method="POST" action="../cgi-bin/authenticate.cgi">
             <table>
              <tr class="form_login">
                  <td> user name: </td> <td> <input name="userName" type="text"> </td>
              </tr>
              <tr class="form_login">
                  <td> password:  </td> <td> <input name="userPass" type="password"> </td>
              </tr>
              <tr class="form_login">
                  <td colspan="2"> <input type="submit" value="Submit"> <input type="reset"> </td>
              </tr>
              <tr class="form_login">
                  <td> Not Registered?   Register <a href="$::URL_PATHS->{REGISTRATION_HTM}"> here </a> </td>
              </tr>
              </table>
          </form>
	<span class="errtext"> <p> $errstr </p> </span>
        </div>
</div>

OUT_HTML
   print $out_buffer;
   print StockUtil::footerHtml();
}
















1;
