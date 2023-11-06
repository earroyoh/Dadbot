import os, logging, io, json, warnings
logging.basicConfig(level="INFO")
warnings.filterwarnings('ignore')

import sys
python = sys.executable

import asyncio
from sanic import Blueprint, response, Sanic
from sanic.request import Request, RequestParameters
from sanic_cors import CORS, cross_origin
from jinja2 import Template
import ssl
import constant

def render_template(html_name, **args):
    with open(os.path.join(os.path.dirname(__file__), 'rasadjango/dadbot/templates', html_name), 'r') as f:
        html_text = f.read()
    template = Template(html_text)
    return response.html(template.render(args))

app = Sanic(__name__)
app.static('/static/', './rasadjango/dadbot/static/', name="static")
app.static('/favicon.ico', './rasadjango/dadbot/static/favicon.ico', name="favicon")
app.static('/audios', './rasadjango/dadbot/audios', name="audios")

# Enable CORS
CORS(app, resources={r"/*": {"origins": ["https://" + constant.DADBOT_WEB_URL ,
    "https://" + constant.DADBOT_WEB_URL + ":" + constant.INGRESS_PORT ,
    "https://" + constant.DADBOT_WEB_URL + ":" + constant.SPEAKER_API_PORT]}}
)

@app.get("/health", name="health")
async def health(request: Request):
    return response.json({"status": "ok"})

@app.get("/", name="root")
async def index(request: Request):
    return render_template('chitchat.html')

config = {}
config["audios"] = "./rasadjango/dadbot/audios"

@app.route("/audios/<user>", methods=['GET', 'POST', 'OPTIONS'], name="user")
def handler(request: Request, user):

    wavaudio = request.files.get("files")

    audio_file = os.path.join(config["audios"], "{}_synthesis.wav".format(user))
    with open(audio_file, 'wb') as f:
        f.write(wavaudio.body)
        f.close()

    return response.json({"file_received": "ok"}, headers={'Allow-Access-Control-Headers': 'x-requested-with', \
                                                           'Allow-Access-Control-Origin': 'https://' + constant.DADBOT_WEB_URL + ':' + constant.INGRESS_PORT})

if __name__ == '__main__':

    # HTTP server (ngrok tunnel)
    #app.run(host='0.0.0.0', port=8000, workers=1)

    # HTTPS server, in order getUserMedia to work
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.verify_mode = ssl.CERT_OPTIONAL
    context.load_cert_chain('./dadbot.crt', './dadbot.key')

    app.run(host='0.0.0.0', port=int(constant.INGRESS_PORT), workers=4, ssl=context, debug=True)
