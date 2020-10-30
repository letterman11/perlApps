var HTTP = {};

HTTP._factories = [
	function() { return new XMLHttpRequest(); },
	function() { return new ActiveXObject("Msxml2.XMLHTTP"); },
	function() { return new ActiveXObject("Microsoft.XMLHTTP"); }
	];


HTTP._factory = null;



HTTP.newRequest = function() {
	if (HTTP._factory != null) return HTTP._factory();

	for(var i = 0; i < HTTP._factories.length; i++) {
		try {
			var factory = HTTP._factories[i];
			var request = factory();
			if (request != null) {
				HTTP._factory = factory;
				return request;
		    	}
		}	
		catch(e) {
			continue;
		}
	}

	HTTP._factory = function() {
		throw new Error("XMLHttpRequest not supported");
	}
	HTTP._factory();
}

var Jax = {

    pingIntervalTime: 5000,
    pingCancelID: null,
    pingURL: "/chatterBox/cgi-bin/jax_ping_msg_server.cgi",
    serverURL: "/chatterBox/cgi-bin/jax_server.cgi",
    serverAuthURL: "/chatterBox/cgi-bin/jax_authenticate.cgi",
    serverRegURL: "/chatterBox/cgi-bin/jax_registration.cgi",
    pingPostString: null,
    responseText: null,
    responseStatusText: null,

    startAjaxPing: function(userID,roomID) {
	this.pingPostString = "req=ajaxPing"; 
	this.pingPostString += "&userID=" + encodeURIComponent(userID) + "&" + "roomID=" + encodeURIComponent(roomID);
	this.pingCancelID = setInterval(Jax.pingServerForData, Jax.pingIntervalTime);

    },

    pingServerForData: function() {

	request = HTTP.newRequest();		
	request.onreadystatechange = function() {
		if(request.readyState == 4) {
			if(request.status == 200) {
				chatPane.setPane(request.responseText);
				userPane.setPane(request.responseText);
			} 
			else	
			{
				alert(request.statusText);
			}
		}


	};

	request.open("POST", Jax.pingURL);
	request.setRequestHeader("Content-Type",
					"application/x-www-form-urlencoded");

	request.send(Jax.pingPostString);


    },

    jaxCallPost: function(url,data,func,errfunc,async) {

        request = HTTP.newRequest();
        request.onreadystatechange = function() {
                if(request.readyState == 4) {
                        if(request.status == 200) {
				
				Jax.responseText = request.responseText;
				func();
                        }
                        else
                        {
				Jax.responseStatusText = request.statusText;
				errfunc();
                        }
                }

        };

        request.open("POST", url, async);
        request.setRequestHeader("Content-Type",
                                        "application/x-www-form-urlencoded");
        request.send(data);

    },

    jaxCallGet: function(url,func,errfunc,async) {

        request = HTTP.newRequest();
        request.onreadystatechange = function() {
                if(request.readyState == 4) {
                        if(request.status == 200) {
				
				func();
                        }
                        else
                        {
				errfunc();
                        }
                }

        };

        request.open("GET", url, async);
        request.send(null);

    }


};
