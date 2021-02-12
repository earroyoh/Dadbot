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

action_endpoint = EndpointConfig(url="http://localhost:5055")
agent = Agent.load(model_directory,  interpreter=os.path.join(model_directory, "nlu"), action_endpoint=action_endpoint)

# NVIDIA TTS dependencies
#os.system("git clone https://github.com/NVIDIA/tacotron2.git")
#os.system("git clone https://github.com/NVIDIA/apex.git")
#os.system("cd tacotron2; git submodule init; git submodule update")
#os.system("git clone https://github.com/DeepLearningExamples.git")
#os.system("ln -s DeepLearningExamples/CUDA-Optimized/FastSpeech/fastspeech fastspeech")

import asyncio
from sty import fg, bg, ef, rs
from wtforms import Form, StringField, validators
from django import forms

class InputForm(Form):
    a = StringField(label=u'Texto', validators=[validators.InputRequired()])

class ChatInputForm(forms.Form):
   chatinput = forms.CharField(max_length = 100)

from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from typing import Awaitable
from jinja2 import Template

def render_template(html_name, **args):
    with open(os.path.join(os.path.dirname(__file__), 'templates', html_name), 'r') as f:
        html_text = f.read()
    template = Template(html_text)
    return HttpResponse(template.render(args))

@csrf_exempt
# Create your views here.
def index(request):

    #form = InputForm(request.POST)
    form = ChatInputForm(request.POST)
    result = "Inicio"
    return render_template('chitchat.html', form=form, result=result)
    #return render_template('form.html', form=form, result=result)
