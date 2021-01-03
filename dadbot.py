import os, logging, io, json, warnings
logging.basicConfig(level="INFO")
warnings.filterwarnings('ignore')

import sys
python = sys.executable

import asyncio
#from sanic import Blueprint, response, Sanic
from sanic import Blueprint, response, Sanic
from sanic.request import Request
from jinja2 import Template

def render_template(html_name, **args):
    with open(os.path.join(os.path.dirname(__file__), 'rasadjango/dadbot/templates', html_name), 'r') as f:
        html_text = f.read()
    template = Template(html_text)
    return response.html(template.render(args))

app = Sanic(__name__)
app.static('/static', './rasadjango/dadbot/static')
app.static('/favicon.ico', './rasadjango/dadbot/static/favicon.ico')
app.static('/audios', './rasadjango/dadbot/audios')
@app.route('/', methods = ['GET', 'POST'])

async def index(request):

    if request.method == 'GET':
        return render_template('chitchat.html')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
