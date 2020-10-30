var TRUE = 1
var FALSE = 0
var LoginFormVisible = FALSE
var QueryFormVisible = FALSE
var stockIDLen = 10	
var SORT_PRICE = 0
var SORT_ORDER = 0
var SORT_DATE = 0
var CRITERION_DEFAULT_PAGE = 1
var handle = parent.top.document;


function init()
{

   stockSessionID = getCookie('stockSessionID');

  if ((stockSessionID != null && stockSessionID != 'null')) {
      document.getElementById('stockApp_description').style.display='none';
      document.getElementById('sub_left_panel').style.display='block';
      document.getElementById('query').style.display='block';
      document.getElementById('logged_on').style.visibility='visible';
      document.getElementById('stockList_container').style.display='block';
      document.getElementById('stockListResult').src = "/stockApp/cgi-bin/populate_stocklist.cgi";
      parent.top.document.frmStockApp.rowsPerPage.value = 20;

   }
}

function getCookieData(label)
{
   var labelLen = label.length
   var cLen = document.cookie.length
   var i = 0
   var cEnd
   while (i < cLen) {
       var j = i + labelLen
       if (document.cookie.substring(i,j) == label) {
          cEnd = document.cookie.indexOf(";",j)
          if (cEnd == -1) {
             cEnd = document.cookie.length
          }
          return unescape(document.cookie.substring(j,cEnd))
       }
       i++
   }
   return null

}

function getCookie( name ) {
  var start = document.cookie.indexOf( name + "=" );
  var len = start + name.length + 1;
  if ( ( !start ) && ( name != document.cookie.substring( 0, name.length ) ) ) {
    return null;
  }
  if ( start == -1 ) return null;
  var end = document.cookie.indexOf( ";", len );
  if ( end == -1 ) end = document.cookie.length;
  return unescape( document.cookie.substring( len, end ) );

}

function createCookie(name,value,days) {
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		var expires = "; expires="+date.toGMTString();
	}
	else var expires = "";
	document.cookie = name+"="+value+expires+"; path=/";
}

function eraseCookie(name) {
	createCookie(name,"",-1);
}


function tblSort(sortField)
{
	var SORT_CRITERION;

	if (sortField == 'PRICE') 
	{
		SORT_CRITERION = ++top.document.frmStockApp.sortCountPrice.value % 2  ?  'SORT_PRICE_DESC' : 'SORT_PRICE_ASC'
	}
	else if (sortField == 'ORDER')
	{
		SORT_CRITERION = ++top.document.frmStockApp.sortCountOrder.value % 2  ?  'SORT_ORDER_DESC' : 'SORT_ORDER_ASC'
	}
	else if (sortField == 'DATE')
	{
		SORT_CRITERION = ++top.document.frmStockApp.sortCountDate.value % 2  ?  'SORT_DATE_DESC' : 'SORT_DATE_ASC'
	} 

	
	top.document.frmStockApp.sortCriteria.value = SORT_CRITERION;
	

	var sortUrl = "/stockApp/cgi-bin/stockReport.cgi?";	
        sortUrl += "stkName=" +escape(handle.frmStockApp.stkName.value) + "&minPrice=" +handle.frmStockApp.minPrice.value + "&maxPrice=" +handle.frmStockApp.maxPrice.value
       	        + "&minQty=" +handle.frmStockApp.minQty.value + "&maxQty=" +handle.frmStockApp.maxQty.value + "&rowsPerPage=" +handle.frmStockApp.rowsPerPage.value
		+ "&sort=" +handle.frmStockApp.sortCriteria.value;

        handle.getElementById('queryResult').src = sortUrl;

}

function goSubmit()
{  
   if (validateFields() == true)
   {

      var url = "/stockApp/cgi-bin/stockReport.cgi?";
        url += "stkName=" +escape(handle.frmStockApp.stkName.value) + "&minPrice=" +handle.frmStockApp.minPrice.value + "&maxPrice=" +handle.frmStockApp.maxPrice.value
          + "&minQty=" +handle.frmStockApp.minQty.value + "&maxQty=" +handle.frmStockApp.maxQty.value + "&rowsPerPage=" +handle.frmStockApp.rowsPerPage.value;

        document.getElementById('queryResult').contentWindow.location.replace(url);
   }

}

function help_page()
{
   document.getElementById('stockApp_description').style.display='block';
   document.getElementById('sub_left_panel').style.display='none';
   document.getElementById('query').style.display='none';
   document.getElementById('logged_on').style.visibility='visible';
   document.getElementById('stockList_container').style.display='none';
   document.getElementById('stockListResult').src = "/stockApp/cgi-bin/populate_stocklist.cgi";
   parent.top.document.frmStockApp.rowsPerPage.value = 20;


}

function init()
{

   stockSessionID = getCookie('stockSessionID');

  if ((stockSessionID != null && stockSessionID != 'null')) {
      document.getElementById('stockApp_description').style.display='none';
      document.getElementById('sub_left_panel').style.display='block';
      document.getElementById('query').style.display='block';
      document.getElementById('logged_on').style.visibility='visible';
      document.getElementById('stockList_container').style.display='block';
      document.getElementById('stockListResult').src = "/stockApp/cgi-bin/populate_stocklist.cgi";
      parent.top.document.frmStockApp.rowsPerPage.value = 20;

   }
}

function logOut()
{
   for(i=0; i<arguments.length; i++) {
      eraseCookie(arguments[i]);
   }
}


function setStockField(stock,div)
{
        parent.top.document.frmStockApp.stkName.value = stock;
        parent.top.document.getElementById('p_big_stock').innerHTML = stock;
        div.style.zIndex = DIV_INDEX.A;
}

function changeBigStock(form)
{
        parent.top.document.getElementById('p_big_stock').innerHTML = form.frmStockApp.stkName.value.toUpperCase();

}

function validateFields()
{
   if(handle.frmStockApp.stkName.value == "" || handle.frmStockApp.stkName.value == "undefined" || handle.frmStockApp.stkName.value == null ||
    handle.frmStockApp.stkName.value == "null")
   {
       alert("Must Supply a Stock Symbol");
       return false;
   }
   else
   {
       return true;
   }

}

function clearFields(handler)
{

   handle.frmStockApp.stkName.value="";
   handle.frmStockApp.minPrice.value="";
   handle.frmStockApp.maxPrice.value="";
   handle.frmStockApp.minQty.value="";
   handle.frmStockApp.maxQty.value="";
   handle.frmStockApp.rowsPerPage.value="";
}

function giveTop(div)
{
        div.style.zIndex = 100;
}


