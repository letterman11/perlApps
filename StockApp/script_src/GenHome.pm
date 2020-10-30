package GenHome;

use strict;
use CGI qw /:standard/;

sub new
{
	my $self = {};
	my $class = shift;
	$self->{COOKIES} = shift;
	bless ($self,$class);
	return $self;

}


sub display
{
	my $self = shift;
	my $cookieList = $self->{COOKIES};
	my $out_buffer=();

	print header(-cookie=>$cookieList);
	
	$out_buffer = <<"OUT_HTML";
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<HTML>
  <HEAD>
    <TITLE>Stock Query Application </TITLE>
        <LINK href="$::URL_PATHS->{MAINSTYLE_CSS}" rel="stylesheet" type="text/css">
        <LINK href="$::URL_PATHS->{ICON}" rel="icon">
        <LINK href="$::URL_PATHS->{ICON_SHORT}" rel="icon">
        <script language="Javascript" src="$::URL_PATHS->{COMMON_JS}"> </script>
    </HEAD>
<BODY onload="init()">

<div id="main">
        <div id="banner">
         <a href="$::URL_PATHS->{STOCKAPP}">    <img id="banner_image" src="$::URL_PATHS->{BANNER_IMAGE}">  </a>
         <a href="$::URL_PATHS->{NEWSITE_HTM}">    <img id="banner_image2" src="$::URL_PATHS->{BANNER_IMAGE2}">  </a>
        </div>

	<div id="logged_on" style="visibility:visible">
         <span class="form_login">  
	   	 <a href=javascript:init();> app </a> |  <a href=javascript:help_page();> help page </a>  
	 </span>
	</div>
</div>

<div id="sub_left_panel" style="display:none">
   <div id="queryForm">
       <form id="frmStockApp" name="frmStockApp">
        <table class="form_query">
          <tr>
           <td>Stock Name: </td> <td> <input name="stkName" type="text" onBlur="changeBigStock(document);"> </td>
           </tr>
          <tr>    
           <td>Min Price: </td> <td> <input name="minPrice" type="text"></td>
          </tr>
          <tr>
            <td>Max Price: </td> <td><input name="maxPrice" type="text"></td>
          </tr>
          <tr>
           <td>Min Quantity: </td> <td><input name="minQty" type="text"></td>
          </tr>
          <tr>
           <td> Max Quantity: </td> <td><input name="maxQty" type="text"></td>
         </tr>
         <tr>
            <td> # of rows:  </td> <td> <select id="rowsPerPage" name="rowsPerPage">
	        <option value="10">10</option>
       		<option value="15">15</option>
      		<option value="20">20</option>
      		<option value="25">25</option>
        	<option value="30">30</option>
        	<option value="50">50</option>
	</td>
         </tr>
         <tr>
           <td> <input type="button" name="btsubmit" value="SUBMIT" onClick="goSubmit()">  </td>
           <td> <input type="button" name="btclear" value="CLEAR" onClick="clearFields(window.document)">  </td>
         </tr>
          <tr>
           <td> <input name="sortCriteria" type="hidden"> </td> 
	   <td> <input name="sortCountPrice" type="hidden"> <input name="sortCountOrder" type="hidden"> <input name="sortCountDate" type="hidden"></td>
         </tr>
        </table>
    </form>
   </div>
   <div id="big_stock">
 	<p id="p_big_stock">      </p>
   </div>

</div>

<div id="stockApp_description">
   <h4 id="description_header"> DCQuery is a demo stock order lookup application, that interfaces with a database of mock stock orders. <br>
        The interface is broken down into three components: Criterion Pane, Stock Selection Pane, and Report Pane. <br>
        To use the application you must register via the link above.
   </h4>

  <div class="help_description_container">
   <div class="help_description">
     <h4> Criterion Pane </h4>
     <p> Stock orders can be queried and filtered by limit price and quantity, with upper and lower ranges designated for both.  The number of rows returned can be selected via option dialog.
     </p>
   </div>
   <div class="help_description">
     <h4> Stock Selection Pane </h4>
     <p>  All available stocks can be chosen from this pane. Once selected it will populate the Criterion Pane and will also be displayed in large bold beneath the Criterion Pane.
     </p>
   </div>
   <div class="help_description">
     <h4> Report Pane </h4>
     <p> Orders for a stock are displayed here and can be sorted by either limit price, quantity or date.
     </p>
   </div>
  </div>

   <script language="Javascript" type="text/javascript">
    if (window.screen.width <= 1024) {
       document.write( '  <div id="small_help_pane"> ' +
      ' </div> ');

    } else {
     document.write( '  <div id="large_help_pane"> ' +
     ' </div> ');
   }
   </script>
</div>


 <div id="stockList_container" style="display:none">
     <iframe id="stockListResult" name="stocklistframe" src="" height= "400"  width="225" frameborder="0" marginheight="0" marginwidth="5" >
     </iframe>
   </div>
   <script language="Javascript" type="text/javascript">
    if (window.screen.width <= 1024) {
       document.write( '  <div id="query" style="visibility:visible"> ' +
           '<iframe id="queryResult" name="queryframe" height= "650" src="" width="475" frameborder="0" marginheight="0" marginwidth="5" > ' +
        ' </iframe> ' +
      ' </div> ');
        
    } else {
     document.write( '  <div id="query" style="visibility:visible"> ' +
           '<iframe id="queryResult" name="queryframe" height= "650" src="" width="700" frameborder="0" marginheight="0" marginwidth="5" > ' +
       ' </iframe> ' +
     ' </div> ');
   }
   </script>

<!--
   <div id="query" style="visibility:visible">
     <iframe id="queryResult" name="queryframe" height= "650" src="" width="700" frameborder="0" marginheight="0" marginwidth="5" >
     </iframe>
   </div>
-->



 </BODY>
</HTML>
OUT_HTML
	   print $out_buffer;
}


sub display_footer
{

 print;

}





1;
