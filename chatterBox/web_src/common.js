
var App = {

    host: "",

    PANE: { 
             REGISTRATION: 0,
             LOGIN: 1,
	     MAIN: 2
    },


    initialize: function() {

        roomPane.init();
        userPane.init();
        chatPane.init(); 

	var roomSelected = getCookie('roomSelected');
	var sessionID = getCookie('SessionID');

        if(sessionID != null && sessionID != 'null')
        {   
            App.changePane(document,App.PANE.MAIN);  

            if(roomSelected == null || roomSelected == 'null')
                roomPane.loadRooms();
        }

    },

    suspend: function() {

	var sessionID = getCookie('SessionID');

        if(sessionID == null || sessionID == 'null' || sessionID == undefined || sessionID == 'undefined')
               return; 

        roomPane.logOutRoom();
        document.getElementById('logout_room_box').style.display = 'none';

    },

    logOut: function() {

        roomPane.logOutRoom();
        document.getElementById('logout_room_box').style.display = 'none';

        for(i=0; i<arguments.length; i++) {
                eraseCookie(arguments[i]);
        }

    },

    logOutRoomReload: function() {
        
        App.suspend();
        roomPane.loadRooms();
    },

    changePane: function(doc,pane) {

       if(pane == this.PANE.REGISTRATION)
       {
                doc.getElementById('landing_panel').style.display = 'none';
                doc.getElementById('main_sub_panel').style.display = 'none';
                doc.getElementById('register_panel').style.display = 'block';

       }
       else if(pane == this.PANE.LOGIN)
       {
                doc.getElementById('landing_panel').style.display = 'block';
                doc.getElementById('register_panel').style.display = 'none';
                doc.getElementById('main_sub_panel').style.display = 'none';
                doc.getElementById('login').style.display = 'block';
                doc.getElementById('logged_on').style.display = 'none';

       }
       else
       {
                doc.getElementById('landing_panel').style.display = 'none';
                doc.getElementById('register_panel').style.display = 'none';
                doc.getElementById('main_sub_panel').style.display = 'block';
                doc.getElementById('login').style.display = 'none';
                doc.getElementById('logged_on').style.display = 'block';
                App.displayLoggedOn();
                roomPane.loadRooms();
		userPane.userID = getCookie('UserID');
       }


    },

    displayLoggedOn: function() {

        var userID = getCookie('UserID');
        var spanLoggedOn = document.getElementById('form_login');
        spanLoggedOn.innerHTML = userID + " LOGGED IN | " +
        " <a href=\"javascript:App.changePane(document,App.PANE.LOGIN)\" style=\"margin-top:10px;\" " +
	"  onclick=\"App.logOut('UserID','SessionID','Instance','roomSelected')\" target=\"_top\" > LOG OUT </a> ";
    }

};


var Utility = {

    emailValidation:  /^\w+[\w.]+?\w+@\w+[\w.]+?\.{1}\w+\s*$/,
    passLen:  6,
    userLen:  6,
    phoneLen:  10,
    zipcodeLen: 5,


    validateRegistration: function(regForm) {

        var state = true;
        this.clearValidationRegistration(regForm);
        
        if (! this.emailValidation.test(regForm.email.value)) {
            document.getElementById("val_email").style.visibility = "visible";
            state = false
        }
        
        if(regForm.userName.value.length < this.userLen) {
            document.getElementById("val_username").style.visibility = "visible";
            state = false
        }
        
        if(regForm.password.value.length < this.passLen) {
            document.getElementById("val_password").style.visibility = "visible";
            state = false
        }
        
        return state;
        
    },

    clearValidationRegistration: function(regForm) {

        document.getElementById("val_email").style.visibility = "hidden";
        document.getElementById("val_username").style.visibility = "hidden";
        document.getElementById("val_password").style.visibility = "hidden";

    },


    processSignInForm: function(form) {

        document.getElementById("err_text").innerHTML =  "";
        var i;
        var request;
        var postString = "";
        var frm = form;
        var url = App.host + Jax.serverAuthURL;

        var frmElements = form.elements;

        for (i=0; i < frmElements.length-1; i++)
        {
                postString += encodeURIComponent(frmElements[i].name) + "=" + encodeURIComponent(frmElements[i].value) + "&";
        }
        postString += encodeURIComponent(frmElements[i].name) + "=" + encodeURIComponent(frmElements[i].value);
        postString = postString.replace(/%20/g,"+");

        Jax.jaxCallPost(url, postString,
                                function() {  setTimeout('App.changePane(document,App.PANE.MAIN)',500); },
                                function() {  document.getElementById("err_text").innerHTML =  Jax.responseStatusText; },
                                 true);

    },
        
    clearSignInForm: function(form) {

        form.userName.value = "";
        form.userPass.value = "";
    },
 
    processRegForm: function(form) {

        if(!this.validateRegistration(form)) return;

        var i;
        var request;
        var postString = "";
        var url = App.host + Jax.serverRegURL;
        var frmElements = form.elements;

        for (i=0; i < frmElements.length-1; i++)
        {
                postString += encodeURIComponent(frmElements[i].name) + "=" + encodeURIComponent(frmElements[i].value) + "&";
        }

        postString += encodeURIComponent(frmElements[i].name) + "=" + encodeURIComponent(frmElements[i].value);
        postString = postString.replace(/%20/g,"+");



        Jax.jaxCallPost(url, postString,
                                        function() {  document.getElementById("reg_response").innerHTML = "<h3>" + Jax.responseText + " </h3> "; },
                                        function() { document.getElementById("reg_response").innerHTML = " <h3>" + Jax.responseStatusText + " </h3> "; },
                                        true);

    },

    processSend: function(sendMsg) {

        var request;
        var postString = "";
        var url = App.host + Jax.serverURL;
        var frmElements = sendMsg.elements;
        var UserID = getCookie('UserID');
        var roomSelected = getCookie('roomSelected');

        frmElements[0].value = frmElements[0].value.replace(/\n/g," ")

        postString  = "req=sendMsg&";
        postString += encodeURIComponent(frmElements[0].name) + "=" + encodeURIComponent(frmElements[0].value) + "&";
        postString += "userID=" + encodeURIComponent(UserID) + "&" + "roomID=" + encodeURIComponent(roomSelected);
        postString = postString.replace(/%20/g,"+");

        if (roomSelected == null || roomSelected == 'null')
                return;


        this.but_on();
        document.chatInput.msgText.value = "";
        Jax.jaxCallPost(url, postString, function() { }, Utility.errStatus, true);


    },

    but_on: function(obj) {

        var butDiv = document.getElementById('sub_button');
        butDiv.style.backgroundColor = 'gray';
        butDiv.getElementsByTagName("h1")[0].style.color = 'black';


        butDiv.style.color = 'black';
        setTimeout('Utility.but_off()',100);
    },


    but_off: function() {

        var butDiv = document.getElementById('sub_button');
        butDiv.style.backgroundColor = 'black'
        butDiv.getElementsByTagName("h1")[0].style.color = 'gray';
        
    },

    but_on2: function() {

        var butH2 = document.getElementById('sub1');
        butH2.style.backgroundColor = 'gray';
        butH2.style.color = 'black';

        setTimeout('Utility.but_off2()',200);
    },

    but_off2: function() {

        var butH2 = document.getElementById('sub1');
        butH2.style.backgroundColor = 'black';
        butH2.style.color = 'gray';
    },


    errStatus: function() {

        alert(request.statusText);
    }

        
};

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

