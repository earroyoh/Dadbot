import os, logging, io, json, warnings
logging.basicConfig(level="INFO")
warnings.filterwarnings('ignore')

import sys
python = sys.executable

# In your environment run:
#os.system("python -m spacy download es_core_news_md")
#os.system("python -m spacy link es_core_news_md es --force")

import rasa
from rasa.model import get_model
from rasa.shared.nlu.training_data.loading import load_data
from rasa.shared.core.slots import Slot, TextSlot
from rasa.shared.core.domain import Domain
from rasa.nlu import config, utils
from rasa.nlu.components import ComponentBuilder
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.model import Interpreter, Trainer, TrainingData
from rasa.nlu.components import Component
from rasa.nlu.tokenizers.tokenizer import Token
from rasa.utils.tensorflow.constants import ENTITY_RECOGNITION
import spacy

#spacy_parser = spacy.load('es_core_news_md')
#nlp = spacy.load('es')

# loading the nlu training samples
training_data = load_data("data/nlu/nlu.yml")

# trainer to educate our pipeline
trainer = Trainer(config.load("config.yml"))

# train the model!
#interpreter = trainer.train(training_data)

# store it for future use
model_directory = get_model("./models/")

#Starting the Bot
from rasa.core.agent import Agent
from rasa.core.utils import EndpointConfig

action_endpoint = EndpointConfig(url="http://localhost:5055/webhook")
agent = Agent.load(model_directory,  interpreter=os.path.join(model_directory, "nlu"), action_endpoint=action_endpoint)

import asyncio
from sty import fg, bg, ef, rs
from wtforms import Form, StringField, validators

class InputForm(Form):
    chatinput = StringField(
        label='Texto', default=u'',
        validators=[validators.InputRequired()])

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

    form = InputForm(request.form)
    result = "Inicio"
    if request.method == 'GET':
        return render_template('chitchat.html', form=form, result=result)
        #return render_template('form.html', form=form, result=result)
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
