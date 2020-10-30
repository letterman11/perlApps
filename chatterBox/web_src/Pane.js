

var chatPane = {

    paneDiv: null,   

    init: function() {
      this.paneDiv = document.getElementById('chat_panel');
      this.chat = document.getElementById('chat_input'); // Fix for extra spaces in send box
      this.chat.elements[0].value = this.chat.elements[0].value.replace(/\s/g,""); // Fix for extra spaces in send box
    }, 

    setPane: function(responseObj) {

       var dataSource;

       try {
	       dataSource = JSON.parse(responseObj);
       }
       catch (ex) {
		return;
       }

       if (dataSource.messages == null || dataSource.messages == 'null' || dataSource.messages == undefined || dataSource.messages == 'undefined')
                return;

       for(i=0; i < dataSource.messages.length; i++)
       {
                var newChatMsgDiv = document.createElement("div");
                var newSpan = document.createElement("span");
                newSpan.style.fontWeight = "bold";
                var userSpanTxtNode = document.createTextNode(dataSource.messages[i].user_id + ": ");
                newSpan.appendChild(userSpanTxtNode);
                var msgStr = dataSource.messages[i].msg_text;
                var userTxtNode = document.createTextNode(msgStr);
                newChatMsgDiv.appendChild(newSpan);
                newChatMsgDiv.appendChild(userTxtNode);

                newChatMsgDiv.className = chatPane.paneDiv.childNodes.length % 2 ? ' chatMsgDiv1' : ' chatMsgDiv2';
                chatPane.paneDiv.appendChild(newChatMsgDiv);
       }
       newChatMsgDiv.scrollIntoView();

   },

    deletePane: function() {

       while(chatPane.paneDiv.hasChildNodes())
       {
               chatPane.paneDiv.removeChild(chatPane.paneDiv.firstChild);
       }

   }


};


var userPane = {

    paneDiv: null,
    userID: null,

    init: function() {
         this.paneDiv = document.getElementById('bot_disp_con');
    },

    setPane: function(responseObj) {

        userPane.deletePane();
    
	var dataSource;

	try {
        	dataSource = JSON.parse(responseObj);
	}
	catch (ex) {
	//	alert("Exception text" + ex.message );
		return;
        }

        if (dataSource.msg_user_ids == null || dataSource.msg_user_ids == 'null' || dataSource.msg_user_ids == undefined || dataSource.msg_user_ids == 'undefined')
                return;

        for(i=0; i < dataSource.msg_user_ids.length; i++)
        {
                if(dataSource.msg_user_ids[i] == userPane.userID)
                        continue;
                var newUserDiv = document.createElement("div");
                var userTxtNode = document.createTextNode(dataSource.msg_user_ids[i]);
                newUserDiv.appendChild(userTxtNode);

                newUserDiv.className = i % 2 ? ' userDiv1' : ' userDiv2';
                userPane.paneDiv.appendChild(newUserDiv);
        }


   }, 

    deletePane: function() {

        while(userPane.paneDiv.hasChildNodes())
        {
                userPane.paneDiv.removeChild(userPane.paneDiv.firstChild);
        }

    }


};


var roomPane = {

    paneDiv: null,
    userID: null,


    init: function() {
        this.paneDiv = document.getElementById('top_sel_con');
    },

    loadRooms: function() {
        
        this.userID = getCookie('chatUserID');
	App.sessionID = getCookie('chatSessionID');

	roomPane.deletePane();
        var url = App.host + Jax.serverURL + "?req=roomIDs";
        Jax.jaxCallGet(url, function() { roomPane.loadRoomPane(request.responseText); }, Utility.errStatus, true);

    },

    loadRoomPane: function(responseObj) {

        var roomArray = JSON.parse(responseObj);

        for(i=0;  i < roomArray.length; i++)
        {
                var newRmDiv = document.createElement("div");
                var rmTxtNode = document.createTextNode(roomArray[i]);
                newRmDiv.appendChild(rmTxtNode);

                newRmDiv.className = i % 2 ? ' roomDiv1' : ' roomDiv2';

                if(window.attachEvent)
                {
                        newRmDiv.attachEvent('onclick', roomPane.logIntoRoom);
                }
                else
                {
                        newRmDiv.addEventListener('click', roomPane.logIntoRoom, false);
                }

                roomPane.paneDiv.appendChild(newRmDiv);
        }


    },

    logIntoRoom: function() {

        var roomDiv;

        if(window.attachEvent)
        {
                roomDiv = window.event.srcElement;
        }
        else
        {
                roomDiv = this;
        }


        var url = App.host + Jax.serverURL;

        var postString  = "req=roomLogin&";
        postString += "userID=" + encodeURIComponent(roomPane.userID) + "&";
        postString += "roomID=" + encodeURIComponent(roomDiv.firstChild.data);

        Jax.jaxCallPost(url, postString,
                        function() {
                                createCookie('roomSelected', roomDiv.firstChild.data);
                                roomPane.setPane(roomDiv.firstChild.data);
                                Jax.startAjaxPing(roomPane.userID,roomDiv.firstChild.data);
                        },
                        Utility.errStatus,
                        true);

    },

    logOutRoom: function() {

        var roomSelected = getCookie('roomSelected');

        var postString;

        while(roomPane.paneDiv.hasChildNodes())
        {

		if(window.addEventListener)
		{
                        roomPane.paneDiv.firstChild.removeEventListener("click", roomPane.logIntoRoom, false);
		}
		else
		{
                        roomPane.paneDiv.firstChild.detachEvent("onclick", roomPane.logIntoRoom);
		}

/*
                if(window.attachEvent)
                {
                        roomPane.paneDiv.firstChild.detachEvent("onclick", roomPane.logIntoRoom);
                }
                else
                {
                        roomPane.paneDiv.firstChild.removeEventListener("click", roomPane.logIntoRoom, false);
                }
*/
                roomPane.paneDiv.removeChild(roomPane.paneDiv.firstChild);
        }

        var url = App.host + Jax.serverURL;

        postString  = "req=roomLogout&";
        postString += "userID=" + encodeURIComponent(roomPane.userID) + "&";
        postString += "roomID=" + encodeURIComponent(roomSelected);

        eraseCookie('roomSelected');
	
        /*-------------------------------------------------------------------
        Important functional code:
        logging out of room automatically deletes the chat pane and user pane 
	---------------------------------------------------------------------*/
        chatPane.deletePane();
        userPane.deletePane();

        if(Jax.pingCancelID)
                clearInterval(Jax.pingCancelID);

        Jax.jaxCallPost(url, postString, function() { document.getElementById('logout_room_box').style.display = 'none'; }, Utility.errStatus, false);

    },

    setPane: function(roomDivText) {

        roomPane.deletePane();
        var newRmDiv = document.createElement("div")
        var rmTxtNode = document.createTextNode(roomDivText);
        newRmDiv.appendChild(rmTxtNode);
        newRmDiv.className = ' roomDiv1';

        roomPane.paneDiv.appendChild(newRmDiv);

        var rmLogOut = document.getElementById('logout_room_box');
        rmLogOut.style.display = 'block';

    },

    deletePane: function() {

        while(roomPane.paneDiv.hasChildNodes())
        {


                if(window.addEventListener)
		{
                        roomPane.paneDiv.firstChild.removeEventListener("click", roomPane.logIntoRoom, false);
		}
		else
		{

                        roomPane.paneDiv.firstChild.detachEvent("onclick", roomPane.logIntoRoom);
		}
/*
                if(window.attachEvent)
                {
                        roomPane.paneDiv.firstChild.detachEvent("onclick", roomPane.logIntoRoom);
                }
                else
                {
                        roomPane.paneDiv.firstChild.removeEventListener("click", roomPane.logIntoRoom, false);
                }
*/
                roomPane.paneDiv.removeChild(roomPane.paneDiv.firstChild);
        }
        document.getElementById('logout_room_box').style.display = 'none';

    }

};
