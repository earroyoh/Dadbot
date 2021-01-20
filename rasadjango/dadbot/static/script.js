$(document).ready(function () {

	//Widget Code
	var bot = '<div class="chatCont" id="chatCont">' +
		'<div class="bot_profile">' +
		'<img src="/static/logo.png" class="bot_p_img">' +
		'<div class="close">' +
		'<i class="fa fa-times" aria-hidden="true"></i>' +
		'</div>' +
		'</div><!--bot_profile end-->' +
		'<div id="result_div" class="resultDiv"></div>' +
		'<div class="chatForm" id="chat-div">' +
		'<div class="spinner">' +
		'<div class="bounce1"></div>' +
		'<div class="bounce2"></div>' +
		'<div class="bounce3"></div>' +
		'</div>' +
		'<input type="text" id="chat-input" autocomplete="off" placeholder="Start Typing here..."' + 'class="form-control bot-txt"/>' +
		'</div>' +
		'</div><!--chatCont end-->' +

		'<div class="profile_div">' +
		'<div class="row">' +
		'<div class="col-hgt col-sm-offset-2">' +
		'<img src="/static/logo.png" class="img-circle img-profile">' +
		'</div><!--col-hgt end-->' +
		'<div class="col-hgt">' +
		'<div class="chat-txt">' +
		'' +
		'</div>' +
		'</div><!--col-hgt end-->' +
		'</div><!--row end-->' +
		'</div><!--profile_div end-->';

	$("mybot").html(bot);

	// ------------------------------------------ Toggle chatbot -----------------------------------------------
	$('.profile_div').click(function () {
		$('.profile_div').toggle();
		$('.chatCont').toggle();
		$('.bot_profile').toggle();
		$('.chatForm').toggle();
		document.getElementById('chat-input').focus();
	});

	$('.close').click(function () {
		$('.profile_div').toggle();
		$('.chatCont').toggle();
		$('.bot_profile').toggle();
		$('.chatForm').toggle();
	});




	// on input/text enter--------------------------------------------------------------------------------------
	$('#chat-input').on('keyup keypress', function (e) {
		var keyCode = e.keyCode || e.which;
		var text = $("#chat-input").val();
		if (keyCode === 13) {
			if (text == "" || $.trim(text) == '') {
				e.preventDefault();
				return false;
			} else {
				$("#chat-input").blur();
				setUserResponse(text);
                                var user = new Date().getTime();
				send(user, text);
				e.preventDefault();
				return false;
			}
		}
	});


	//------------------------------------------- Call the RASA API--------------------------------------
	function send(user, text) {


		$.ajax({
			//url: 'http://192.168.1.103:5005/webhooks/voice/webhook', //  RASA API
			url: 'http://f9c563424863.eu.ngrok.io/webhooks/voice/webhook', //  RASA API
			type: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			data: JSON.stringify({
				//"sender": "user_uttered", "message": text, "session_id": "12345678"
				"sender": user, "message": text
			}),
			success: function (data, textStatus, xhr) {
				console.log(data);
				setBotResponse(user, data);

			},
			error: function (xhr, textStatus, errorThrown) {
				console.log('Error in Operation');
				setBotResponse('error');
			}
		});





	}


	//------------------------------------ Set bot response in result_div -------------------------------------
	function setBotResponse(user, val) {
		setTimeout(function () {

			if ($.trim(val) == '' || val == 'error') { //if there is no response from bot or there is some error
				val = 'Sorry I wasn\'t able to understand your Query. Let\' try something else!'
				var BotResponse = '<p class="botResult">' + val + '</p><div class="clearfix"></div>';
				$(BotResponse).appendTo('#result_div');
			} else {

				//if we get message from the bot succesfully
				var msg = "";
				for (var i = 0; i < val.length; i++) {
					msg += '<p class="botResult">' + val[i].text + '</p><div class="clearfix"></div>';
                                        //msg += '<audio src="http://192.168.1.103:8000/audios/' + String(i) + '_' + user + '_synthesis.wav" type="audio/wav" autoplay></audio>';
                                        msg += '<audio src="http://18e854284ff8.eu.ngrok.io/audios/' + String(i) + '_' + user + '_synthesis.wav" type="audio/wav" autoplay></audio>';
				}
                                BotResponse = msg;
				$(BotResponse).appendTo('#result_div');
			}
			scrollToBottomOfResults();
			hideSpinner();
                        cache.delete(request, {options}).then(function(found) {
                            // your cache entry has been deleted if found
                        });
		}, 500);
	}


	//------------------------------------- Set user response in result_div ------------------------------------
	function setUserResponse(val) {
		var UserResponse = '<p class="userEnteredText">' + val + '</p><div class="clearfix"></div>';
		$(UserResponse).appendTo('#result_div');
		$("#chat-input").val('');
		scrollToBottomOfResults();
		showSpinner();
		$('.suggestion').remove();
	}


	//---------------------------------- Scroll to the bottom of the results div -------------------------------
	function scrollToBottomOfResults() {
		var terminalResultsDiv = document.getElementById('result_div');
		terminalResultsDiv.scrollTop = terminalResultsDiv.scrollHeight;
	}


	//---------------------------------------- Spinner ---------------------------------------------------
	function showSpinner() {
		$('.spinner').show();
	}

	function hideSpinner() {
		$('.spinner').hide();
	}

});
