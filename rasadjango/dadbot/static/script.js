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
		'<input type="text" id="chat-input" autocomplete="off" placeholder="Empieza a escribir aquí o pulsa para hablar..."' + 'class="form-control bot-txt"/>' +
		'<button id="speech" class="speech-input m-left type2">' +
		'<audio id="audio"></audio>' +
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
                if (!user) {
					var user = Math.floor((1 + Math.random()) * 0x1000000).toString(16);
				}
				send(user, text);
				e.preventDefault();
				return false;
			}
		}
	});

	// on input/speech pressed----------------------------------------------------------------------------------
	if (!user) {
		var user = Math.floor((1 + Math.random()) * 0x1000000).toString(16);
	}
	const audio_path = './rasadjango/dadbot/audios/' + user;	
	var mediaRecorder;
	var recordedChunks = [];
	var mic_not_pressed = true;

	// Mouse over the microphone
	$('.speech-input.m-left.type2').mouseover( function () {
		let micbutton = document.getElementById("speech");
		let audio = document.getElementById("audio");
		if (mic_not_pressed) {
			micbutton.style.color = "white";	
			micbutton.style.backgroundColor = "#574ae2";	
		}	
	});		

	// Mouse leave the microphone
	$('.speech-input.m-left.type2').mouseleave( function () {
		let micbutton = document.getElementById("speech");
		let audio = document.getElementById("audio");
		if (mic_not_pressed) {
			micbutton.style.color = "#574ae2";	
			micbutton.style.backgroundColor = "white";	
		}
	});	

	// Microphone pressed
	$('.speech-input.m-left.type2').click( function () {
                mic_not_pressed = false;
		let micbutton = document.getElementById("speech");
		let audio = document.getElementById("audio");

		$("#chat-input").blur();
		console.log("Microphone pressed");

		if (!mediaRecorder || (mediaRecorder.state == "inactive")) {
			// Not recording yet
			// Change microphone appearance
			micbutton.style.color = "red";	
			micbutton.style.backgroundColor = "black";	

			navigator.getMedia = ( navigator.getUserMedia ||
						navigator.webkitGetUserMedia ||
						navigator.mozGetUserMedia || navigator.mediaDevices.getUserMedia );

			// Define recorder and start recording
			navigator.getMedia({video: false, audio: true}, function (stream) {
				audio.srcObject = stream;
				audio.captureStream = audio.captureStream || audio.mozCaptureStream;
				mediaRecorder = new MediaRecorder(stream, { mimetype: 'audio/ogg; codecs=0' });
				mediaRecorder.addEventListener('dataavailable', function (blob) {
					if (blob.data && (blob.data.size > 0)) {
						// Append succesive audio chunks
						recordedChunks.push(blob.data);
					} else {
						return;
					}
				});
				// Start recording
				mediaRecorder.start(0);
				console.log("Audio recording");

				}, function () {console.log("Error getMedia");}
			);

		} else {
			// Return microphone to normal appearance
			micbutton.style.color = "#574ae2";	
			micbutton.style.backgroundColor = "white";	

			// Stop recording
			mediaRecorder.stop(0);
			console.log("Audio stopped");

			var newblob = new Blob(recordedChunks, { type: 'audio/ogg; codecs=0;' });
			//console.log(recordedChunks);
			//audio.src = URL.createObjectURL(newblob);

			// Clear tracks to avoid browser going on recording
			const tracks = audio.srcObject.getTracks();
			tracks[0].stop();

			var fd = new FormData();
			fd.append('files', newblob, audio_path);

			// Uncomment if you want to save locally recorded audio
			//var url = URL.createObjectURL(newblob);
			//var a = document.createElement('a');
			//document.body.appendChild(a);
			//a.style = 'display: none';
			//a.href = url;
			//a.download = 'test.wav';
			//a.click();

			// Send recorded voice to web server
			send_voice(user, fd);
		        showSpinner();

                        mic_not_pressed = true;
			delete mediaRecorder; // Not best practice, but just to reinitialize recorder and avoid cache unwanted effects
			recordedChunks = [];
		};
	});

	//------------------------------------------- Call the RASA API--------------------------------------
	function send_voice(user, data) {

		$.ajax({
			//url: 'https://192.168.1.101:8000/audios/' + user,
			url: 'https://dadbot-web.ddns.net:8000/audios/' + user,
			//url: 'https://df66bb2ad4a9.eu.ngrok.io/audios/' + user,
			type: 'POST',
			headers: {
				'Access-Control-Allow-Methods': 'POST, OPTIONS',
				'Access-Control-Allow-Headers': 'x-requested-with'
			},
			data: data,
			processData: false,
			contentType: false,
			dataType: 'json',
			cache: false,
			success: function (data, textStatus, xhr) {
				console.log(data);
				// --STT-- tells voice connector that it has to get recorded voice from web server for specific user
				send(user, "--STT--");
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
			//url: 'https://192.168.1.101:5005/webhooks/voice/webhook', //  RASA API
			url: 'https://dadbot-web.ddns.net:5005/webhooks/voice/webhook', //  RASA API
			//url: 'https://6eaab23a9fd0.eu.ngrok.io/webhooks/voice/webhook', //  RASA API
			type: 'POST',
			headers: {
				'Access-Control-Allow-Methods': 'POST, OPTIONS',
				'Access-Control-Allow-Headers': 'x-requested-with'
			},
			data: JSON.stringify({
				//"sender": "user_uttered", "message": text, "session_id": "12345678"
				"sender": user, "message": text
			}),
			dataType: 'json',
			cache: false,
			success: function (data, textStatus, xhr) {
				console.log(data);
				if (text == "--STT--") {
					setUserResponse(data.text);
					// Send back extracted STT
					send(user, data.text);
				};
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
				val = 'Perdona pero no he entendido tu solicitud. ¡Probemos algo distinto!.';
				var BotResponse = '<p class="botResult">' + val + '</p><div class="clearfix"></div>';
				$(BotResponse).appendTo('#result_div');
			} else {

				//if we get message from the bot succesfully
				var msg = "";
				for (var i = 0; i < val.length; i++) {
					msg = '<p class="botResult">' + val[i].text + '</p><div class="clearfix"></div>';
					//msg += '<audio id="botaudio" src="http://192.168.1.101:8000/audios/' + String(i) + '_' + user + '_synthesis.wav" type="audio/wav" autoplay></audio>';
					msg += '<audio id="botaudio" src="https://dadbot-web.ddns.net:8000/audios/' + String(i) + '_' + user + '_synthesis.wav" type="audio/wav" autoplay></audio>';
					//msg += '<audio id="botaudio" src="https://df66bb2ad4a9.eu.ngrok.io/audios/' + String(i) + '_' + user + '_synthesis.wav" type="audio/wav" autoplay></audio>';
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
			delete BotResponse;
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
