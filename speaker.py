import os, logging, io, json, warnings
logging.basicConfig(level="INFO")
warnings.filterwarnings('ignore')

import sys
python = sys.executable

import asyncio
from sanic import Blueprint, response, Sanic
from sanic.request import Request, RequestParameters
from sanic.response import stream
from sanic_cors import CORS, cross_origin
from jinja2 import Template
import requests
import ssl
import constant

import torch
import sounddevice as sd
from scipy.io.wavfile import write
#from synthesize import synthesize
from sileroSTT import sileroSTT
from sileroTTS import sileroTTS

app = Sanic(__name__)
app.static('/get/', './rasadjango/dadbot/audios/')
app.static('/put/', './rasadjango/dadbot/audios')
app.static('/audios', './rasadjango/dadbot/audios')

logger = logging.getLogger(__name__)

# Enable CORS
#CORS(app, resources={r"/*": {"origins": "{}".format(constant.DADBOT_WEB_URL)}}, methods = ['POST', 'OPTIONS'])
CORS(app, automatic_options=True)

@app.route('/health', methods=['GET'])
async def health(request: Request):
    return response.json({"status": "ok"})

config = {}
config["audios"] = "./rasadjango/dadbot/audios"

@app.route('/get/<user>', methods=['GET', 'POST', 'OPTIONS'])
def handler(request: Request, user):

    # Get recorded user voice through HTTP server
    audio_file = "{}_synthesis.wav".format(user)
    audio_path = os.path.join(
        "./rasadjango/dadbot/audios/", audio_file)

    #url = "https://192.168.1.104:8000/audios/{}".format(audio_file)
    url = "https://{}".format(constant.DADBOT_WEB_URL) + ":{}".format(constant.INGRESS_PORT) + "/audios/{}".format(audio_file)
    #url = "https://df66bb2ad4a9.eu.ngrok.io/audios/{}".format(audio_file)
    r = requests.get(url, verify=False)

    with open(audio_path, 'wb') as f:
        f.write(r.content)

        # Silero STT
        text = sileroSTT(audio_path)
        f.close()
    
    return response.json({"sender_id": user, "message": text},
                        headers={'Allow-Access-Control-Headers': 'x-requested-with',
                                 'Access-Control-Allow-Origin': 'https://{}'.format(constant.DADBOT_WEB_URL) + ':{}'.format(constant.INGRESS_PORT)})

@app.route('/put/<user>', methods=['GET', 'POST', 'OPTIONS'])
def handler(request: Request, user):

    # Get botutterance from RASA API
    botutterance = request.json.get("message")
    logger.info(f"Botutterance received: " + botutterance)

    # Select the TTS model to use via definition in credentials.yml
    #if (self.tts == "nvidia"):
    #    voice, sr = synthesize(botutterance, self.speaker, self.sigma, self.denoiser)
    #else:
    voice, sr = sileroTTS(botutterance)

    #Stream bot voice through HTTP server
    audio_file = "{}_synthesis.wav".format(user)
    audio_path = os.path.join(
        "./rasadjango/dadbot/audios/", audio_file)
    write(audio_path, sr, voice)

    #url = "https://192.168.1.104:8000/audios/{}".format(user)
    url = "https://{}".format(constant.DADBOT_WEB_URL) + ":{}".format(constant.INGRESS_PORT) + "/audios/{}".format(user)
    #url = "https://df66bb2ad4a9.eu.ngrok.io/audios/{}".format(user)
    with open(audio_path, 'rb') as f:
        files = {"files": (audio_path, f, 'application/octet-stream')}
        r = requests.post(url, files = files, verify=False)
        status = r.json()
        logger.debug(f"File sent " + audio_file + ": " + json.dumps(status["file_received"]))
        f.close()

    return response.json({"file_sent": audio_file},
                        headers={'Allow-Access-Control-Headers': 'x-requested-with',
                                 'Access-Control-Allow-Origin': 'https://{}'.format(constant.DADBOT_WEB_URL) + ':{}'.format(constant.INGRESS_PORT)})


if __name__ == '__main__':

    # HTTP server (ngrok tunnel)
    #app.run(host='0.0.0.0', port=constant.SPEAKER_API_PORT, workers=4)

    # HTTPS server, in order getUserMedia to work
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.verify_mode = ssl.CERT_OPTIONAL
    context.load_cert_chain('./dadbot.crt', './dadbot.key')

    app.run(host='0.0.0.0', port=int(constant.SPEAKER_API_PORT), workers=4, ssl=context)
