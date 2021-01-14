import os, logging, io, json, warnings
logging.basicConfig(level="INFO")
warnings.filterwarnings('ignore')

import sys
python = sys.executable

import asyncio
#from sanic import Blueprint, response, Sanic
from sanic import Blueprint, response, Sanic
from sanic.request import Request
from sanic.response import stream
from jinja2 import Template
import numpy as np

def render_template(html_name, **args):
    with open(os.path.join(os.path.dirname(__file__), 'rasadjango/dadbot/templates', html_name), 'r') as f:
        html_text = f.read()
    template = Template(html_text)
    return response.html(template.render(args))

app = Sanic(__name__)
app.static('/static/', './rasadjango/dadbot/static/')
app.static('/favicon.ico', './rasadjango/dadbot/static/favicon.ico')
app.static('/audios', './rasadjango/dadbot/audios')

@app.get('/')

async def index(request):
    return render_template('chitchat.html')

config = {}
config["audios"] = "./rasadjango/dadbot/audios"

@app.post('/audios/<user>', stream=False)

async def handler(request, user):
    wavaudio = np.array([])
    wavaudio = await request.stream.read()

    audio_file = os.path.join(config["audios"], "{}_synthesis.wav".format(user))
    with open(audio_file, 'wb') as f:
        f.write(wavaudio)
    f.close()

    return response.json({"file_received": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, workers=4)
