function init()
{
   $.ajax({ 
	url:'http://localhost:8080/pollCenter/cgi-bin/poll_server.cgi', 
        type:'post',
	data:"refresh=true",
	success:init_page
   });

}

function poll_graph()
{
   $.ajax({ 
	url:'http://localhost:8080/pollCenter/cgi-bin/graph_server.cgi', 
        type:'post',
	dataType:'json',
	data:"poll_ids=100:101:102:103",
	success:pop_graphs,
	error:except_handle
   });

}

function pop_graphs(jsonObj, textResp)
{
   var jObj = jsonObj;

   jObj[0].options.seriesDefaults.renderer = $.jqplot.BarRenderer;
   jObj[1].options.seriesDefaults.renderer = $.jqplot.BarRenderer;
   jObj[2].options.seriesDefaults.renderer = $.jqplot.BarRenderer;
   jObj[3].options.seriesDefaults.renderer = $.jqplot.BarRenderer;

   jObj[0].options.axes.yaxis.tickOptions.formatString = "%d"; 
   jObj[1].options.axes.yaxis.tickOptions.formatString = "%d"; 
   jObj[2].options.axes.yaxis.tickOptions.formatString = "%d"; 
   jObj[3].options.axes.yaxis.tickOptions.formatString = "%d"; 

   $.jqplot('poll1graph', jObj[0].data, jObj[0].options).redraw(); 
   $.jqplot('poll2graph', jObj[1].data, jObj[1].options).redraw(); 
   $.jqplot('poll3graph', jObj[2].data, jObj[2].options).redraw(); 
   $.jqplot('poll4graph', jObj[3].data, jObj[3].options).redraw(); 

}

         
$(document).ready(function() {                                                                                

   $('#sub_button').click(function() {                                                                     
          $(this).css('color','white');                                                                           
	  $(this).css('background-color', '#330077');
	  setTimeout(function() { $('#sub_button').css('color', '#330077'); $('#sub_button').css('background-color', 'white');}, 200);
	  validate();
   });                                                                                                     

   $('#reset_button').click(reset_button);
   
   var pollCookie = getCookie('pollCenterID');

   if(pollCookie != null && pollCookie != 'null')
   { 		
	poll_graph(); 
   }

});                                

function validate()
{
    var data='';
    var flagFormError;
    var flagCaptchaError;
    var captcha_text;

    $('.pollform').each(function(){
       if(!$(this).find('input[type=radio]:checked').val())
       {
           $(this).find('li:first').css('color', 'red');
	   flagFormError=1; 
       }
       else
       {
           $(this).find('li:first').css('color', 'black');
       }

       data += $(this).find('input:hidden').attr('name') + $(this).find('input:hidden').val(); 
       data += "=" + $(this).find('input[type=radio]:checked').val(); 
       data += "&";
    });

    captcha_text =  $('#submission input:text').val();

    $('#sub_box form p.error').hide()
    if (captcha_text == "" || captcha_text == undefined)
    {
	$('#sub_box form p:first').hide()
	$('#sub_box form p.error').show()
	flagCaptchaError=1
    }

    if(flagFormError) 
  	$('span.error').show();
    else
        $('span.error').hide();

    if(flagFormError || flagCaptchaError)
	return 0;

    data += "captcha_text=" +  encodeURIComponent($('#submission input:text').val());
    
    send_data(data);
}

function reset_button()
{
    $('#reset_button').css('color','white');                                                                           
    $('#reset_button').css('background-color', '#330077');

    setTimeout(function() { $('#reset_button').css('color', '#330077'); $('#reset_button').css('background-color', 'white');}, 300);

    $('.pollform').find('li:first').css('color', 'black');

    $('.pollform').each(function(){
	this.reset();
    });

    $('#sub_box form p:first').show()
    $('.error').hide()
    document.captcha_submit.reset();

}

function reset()
{
    $('.pollform').find('li:first').css('color', 'black');

    $('.pollform').each(function(){
	this.reset();
    });

    $('#sub_box form p:first').show()
    $('.error').hide()
    document.captcha_submit.reset();

}

function init_page(var1,var2)
{
   var url1 = "url('"+var1+"')";
   $('.pollform').find('li:first').css('color', 'black');

   $('.pollform').each(function(){
        this.reset();
   });

   $('#sub_box form p:first').show()
   $('.error').hide()
   document.captcha_submit.reset();
 
   $('#captcha').css('background-image', url1);
   $('#captcha').css('background-position', 'center center');

}

function send_data(sdata)
{
   $.ajax({ 
	url:'http://localhost:8080/pollCenter/cgi-bin/poll_server.cgi', 
	//url:'http://192.168.0.100:8080/pollCenter/cgi-bin/poll_server.cgi', 
        type:'post',
	data:sdata,
	success:done_deal,   
        error:handle_except
   });

}

function done_deal(var1,var2)
{
   var url1 = "url('"+var1+"')";
   $('#captcha').css('background-image', url1);
   $('#captcha').css('background-position', 'center center');
   poll_graph();
   reset();
  
}

function except_handle(xmlReq, statText, errThrow)
{
   alert(xmlReq + " str " + statText);
   alert(" err " + errThrow);

}

function handle_except(xmlObj, statText)
{
   $('#sub_box form p:first').hide()
   $('#sub_box form p.error').show()
   
}

function getCookie(name,path)
{
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

function createCookie(name,value,days)
{
        if (days) {
                var date = new Date();
                date.setTime(date.getTime()+(days*24*60*60*1000));
                var expires = "; expires="+date.toGMTString();
        }
        else var expires = "";
        document.cookie = name+"="+value+expires+"; path=/";
}

function eraseCookie(name)
{
        createCookie(name,"",-1);
}

