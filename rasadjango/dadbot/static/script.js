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
		'<input type="text" id="chat-input" autocomplete="off" placeholder="Empieza a escribir o a hablar aqui..."' + 'class="form-control bot-txt"/>' +
		'<button id="speech" class="speech-input m-left type2">' +
		'<audio autoplay></audio>' +
		'<label for="speech" class="fa fa-microphone fa-3x" aria-hidden="true"/>' +
		'</div><!--chatForm end-->' +
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
                                var user = Math.floor((1 + Math.random()) * 0x1000000).toString(16);
				send(user, text);
				e.preventDefault();
				return false;
			}
		}
	});

	// on input/speech pressed----------------------------------------------------------------------------------
	let mediaRecorder;
	let blobURL;
	let recordedChunks = [];
	let i = 0;
	$('.speech-input.m-left.type2').click(function () {
		$("#chat-input").blur();
		console.log("Microphone pressed");
		if (typeof mediaRecorder === "undefined" ) {
			//$('.speech-input.m-left.type2').style.color = "red";	
			//$('.speech-input.m-left.type2').style.backgroundColor = "black";	

			navigator.getMedia = ( navigator.getUserMedia ||
						navigator.webkitGetUserMedia ||
						navigator.mozGetUserMedia || navigator.mediaDevices.getUserMedia);

			navigator.getMedia({video: false, audio: true}, function(stream) { 
				mediaRecorder = new MediaStreamRecorder(stream);
				mediaRecorder.mimeType = 'audio/wav';
				mediaRecorder.audioChannels = 1;
				mediaRecorder.ondataavailable = function (blob) {
					// POST/PUT "Blob" using FormData/XHR2
					blobURL = URL.createObjectURL(blob);
					body = '<a href="' + blobURL + '">' + blobURL + '</a>';
					if (blob.size > 0) {
						var reader = new FileReader();
						reader.addEventListener('loadend', function () {
							chunk = reader.result;
							recordedChunks.push(chunk);
						});
						reader.readAsArrayBuffer(blob);
						i += 1;
					}
				};
				mediaRecorder.start();
				console.log("Audio recording");
			}, function(error) { console.log("Error getUserMedia"); });

		} else {
			mediaRecorder.stop();
			console.log("Audio stopped");

			const user = Math.floor((1 + Math.random()) * 0x1000000).toString(16);
			const audio_path = './rasadjango/dadbot/audios/' + user;	
			recording = new Blob(recordedChunks, {type: 'audio/wav'});
			//reader = new FileReader();
			//reader.readAsArrayBuffer(recording);
			const data = {"files": (audio_path, recording)};
			console.log(data);

			var url = URL.createObjectURL(recording);
			var a = document.createElement('a');
			document.body.appendChild(a);
			a.style = 'display: none';
			a.href = url;
			a.download = 'test.wav';
			a.click();

			send_voice(user, data);

			delete mediaRecorder; // to undefine for next Microphone pressed
			i = 0;
		};
	});

	//------------------------------------------- Call the RASA API--------------------------------------
	function send_voice(user, data) {

		$.ajax({
			//url: 'http://192.168.1.103:8000/audios',
			url: 'http://dadbot-web:8000/audios/' + user,
			//url: 'https://48fea2d6c3ed.eu.ngrok.io/audios',
			type: 'POST',
			headers: {
				'Access-Control-Allow-Origin': '*',
				'Content-Type': 'application/json; charset=utf-8'
			},
			data: JSON.stringify(data),
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

	//------------------------------------------- Call the RASA API--------------------------------------
	function send(user, text) {


		$.ajax({
			//url: 'http://192.168.1.103:5005/webhooks/voice/webhook', //  RASA API
			url: 'http://dadbot-connector:5005/webhooks/voice/webhook', //  RASA API
			//url: 'https://48fea2d6c3ed.eu.ngrok.io/webhooks/voice/webhook', //  RASA API
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
				val = 'Perdona pero no he entendido tu solicitud. ¡Probemos algo distinto!.'
				var BotResponse = '<p class="botResult">' + val + '</p><div class="clearfix"></div>';
				$(BotResponse).appendTo('#result_div');
			} else {

				//if we get message from the bot succesfully
				var msg = "";
				for (var i = 0; i < val.length; i++) {
					msg = '<p class="botResult">' + val[i].text + '</p><div class="clearfix"></div>';
					//msg += '<audio src="http://192.168.1.103:8000/audios/' + String(i) + '_' + user + '_synthesis.wav" type="audio/wav" autoplay></audio>';
					msg += '<audio id="botaudio" src="http://dadbot-web:8000/audios/' + String(i) + '_' + user + '_synthesis.wav" type="audio/wav" autoplay></audio>';
					//msg += '<audio src="https://27875340f6fc.eu.ngrok.io/audios/' + String(i) + '_' + user + '_synthesis.wav" type="audio/wav" autoplay></audio>';
					BotResponse = msg;
					if (i > 0)
						setTimeout(function() {
				        		$(BotResponse).appendTo('#result_div');
						}, 2000);
					else
						$(BotResponse).appendTo('#result_div');

				}
			}
			hideSpinner();
			scrollToBottomOfResults();
			let cache;
			cache.delete(request, {options}).then(function(found) {
				// your cache entry has been deleted if found
			});
		}, 100);
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
