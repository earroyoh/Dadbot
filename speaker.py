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
CORS(app, resources={r"/*": {"origins": "dadbot-web.ddns.net"}})

@app.route('/health', methods=['GET'])
async def health(request: Request):
    return response.json({"status": "ok"})

config = {}
config["audios"] = "./rasadjango/dadbot/audios"

@app.route('/get/<user>', methods=['POST', 'OPTIONS'])
def handler(request: Request, user):

    # Get recorded user voice through HTTP server
    audio_file = "{}_synthesis.wav".format(user)
    audio_path = os.path.join(
        "./rasadjango/dadbot/audios/", audio_file)

    #url = "https://192.168.1.104:8000/audios/{}".format(audio_file)
    url = "https://dadbot-web.ddns.net:8000/audios/{}".format(audio_file)
    #url = "https://df66bb2ad4a9.eu.ngrok.io/audios/{}".format(audio_file)
    r = requests.get(url, verify=False)

    with open(audio_path, 'wb') as f:
        f.write(r.content)

        # Silero STT
        text = sileroSTT(audio_path)
        f.close()
    
    return response.json({"sender_id": user, "message": text}, headers={'Allow-Access-Control-Headers': 'x-requested-with', 'Allow-Access-Control-Origin': 'dadbot-web.ddns.net'})

@app.route('/put/<user>', methods=['POST', 'OPTIONS'])
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
    url = "https://dadbot-web.ddns.net:8000/audios/{}".format(user)
    #url = "https://df66bb2ad4a9.eu.ngrok.io/audios/{}".format(user)
    with open(audio_path, 'rb') as f:
        files = {"files": (audio_path, f, 'application/octet-stream')}
        r = requests.post(url, files = files, verify=False)
        status = r.json()
        logger.debug(f"File sent " + audio_file + ": " + json.dumps(status["file_received"]))
        f.close()

    return response.json({"file_sent": audio_file}, headers={'Allow-Access-Control-Headers': 'x-requested-with', 'Allow-Access-Control-Origin': 'dadbot-web.ddns.net'})


if __name__ == '__main__':

    # HTTP server (ngrok tunnel)
    #app.run(host='0.0.0.0', port=5006, workers=4)

    # HTTPS server, in order getUserMedia to work
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.verify_mode = ssl.CERT_OPTIONAL
    context.load_cert_chain('./dadbot.crt', './dadbot.key')

    app.run(host='0.0.0.0', port=5006, workers=4, ssl=context)
