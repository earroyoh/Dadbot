import os, logging, io, json, warnings
logging.basicConfig(level="INFO")
warnings.filterwarnings('ignore')

import sys
python = sys.executable

import asyncio
#from sanic import Blueprint, response, Sanic
from sanic import Blueprint, response, Sanic
from sanic.request import Request, RequestParameters
from sanic.response import stream
from sanic_cors import CORS, cross_origin
from jinja2 import Template

def render_template(html_name, **args):
    with open(os.path.join(os.path.dirname(__file__), 'rasadjango/dadbot/templates', html_name), 'r') as f:
        html_text = f.read()
    template = Template(html_text)
    return response.html(template.render(args))

app = Sanic(__name__)
app.static('/static/', './rasadjango/dadbot/static/')
app.static('/favicon.ico', './rasadjango/dadbot/static/favicon.ico')
app.static('/audios', './rasadjango/dadbot/audios')

# Enable CORS
#CORS(app, resources={r"/*"": {"origins": "http://dadbot-web:8000/, http://192.168.1.104:8000/, http://localhost:8000/"}})
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/', methods=['GET'])
async def index(request):
    return render_template('chitchat.html')

config = {}
config["audios"] = "./rasadjango/dadbot/audios"

@app.route('/audios/<user>', methods=['POST', 'OPTIONS'])

def handler(request: Request, user):

    wavaudio = request.files.get("files")

    audio_file = os.path.join(config["audios"], "{}_synthesis.wav".format(user))
    with open(audio_file, 'wb') as f:
        f.write(wavaudio.body)
        f.close()

    return response.json({"file_received": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, workers=4)