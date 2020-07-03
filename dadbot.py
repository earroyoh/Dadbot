import logging, io, json, warnings
logging.basicConfig(level="INFO")
warnings.filterwarnings('ignore')

import sys
python = sys.executable

# In your environment run:
#!{python} -m pip install -U rasa_core==0.14.5 rasa_nlu[spacy];
#!{python} -m pip install spacy==2.2.1

#!{python} -m spacy download es_core_news_md
#!{python} -m spacy link es_core_news_md es --force

import rasa_nlu
import rasa_core
from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer
from rasa_nlu import config
#import spacy

#spacy_parser = spacy.load('es_core_news_md')
#nlp = spacy.load('es')

# loading the nlu training samples
training_data = load_data("data/nlu/nlu-papaito.md")

# trainer to educate our pipeline
trainer = Trainer(config.load("config_simple.yml"))

# train the model!
interpreter = trainer.train(training_data)

# store it for future use
model_directory = trainer.persist("./models/nlu", fixed_model_name="current")

#Starting the Bot
from rasa_core.agent import Agent
from rasa_core.utils import EndpointConfig

action_endpoint = EndpointConfig(url="http://0.0.0.0:5055/webhook")
agent = Agent.load('models/dialogue', interpreter=model_directory, action_endpoint=action_endpoint)

#!git clone https://github.com/NVIDIA/tacotron2.git

from tacotron2.hparams import create_hparams
from tacotron2.model import Tacotron2
from tacotron2.layers import TacotronSTFT, STFT
from tacotron2.audio_processing import griffin_lim
from tacotron2.train import load_model
from tacotron2.text import text_to_sequence
from tacotron2.waveglow.mel2samp import files_to_list, MAX_WAV_VALUE
from tacotron2.denoiser import Denoiser
import numpy as np
import torch

def synthesize(text, voice, sigma=0.6, denoiser_strength=0.05, is_fp16=False):

    hparams = create_hparams()
    hparams.sampling_rate = 22050

    if voice == "papaito":
        voice_model = "nvidia_tacotron2_papaito_300"
    elif voice == "constantino":
        voice_model = "tacotron2_Constantino_600"
    elif voice == "orador":
        voice_model = "checkpoint_tacotron2_29000_es"
    
    checkpoint_path = "/home/debian/workspace/models/" + voice_model
        
    model = load_model(hparams)
    model.load_state_dict(torch.load(checkpoint_path)['state_dict'])
    _ = model.cuda().eval().half()

    waveglow_path = '/home/debian/workspace/models/waveglow_256channels_ljs_v2.pt'
    waveglow = torch.load(waveglow_path)['model']
    _ = waveglow.cuda().eval().half()
    denoiser = Denoiser(waveglow)

    #text="¡Cágate lorito!"
    #with open(filelist_path, encoding='utf-8', mode='r') as f:
    #    text = f.read()

    sequence = np.array(text_to_sequence(text, ['english_cleaners']))[None, :]
    sequence = torch.autograd.Variable(
        torch.from_numpy(sequence)).cuda().long()

    mel_outputs, mel_outputs_postnet, _, alignments = model.inference(sequence)
    #mel = torch.unsqueeze(mel, 0)
    mel = mel_outputs.half() if is_fp16 else mel_outputs
    audio = np.array([])
    with torch.no_grad():
        audio = waveglow.infer(mel, sigma=sigma)
        if denoiser_strength > 0:
             audio = denoiser(audio, denoiser_strength)
        audio = audio * MAX_WAV_VALUE
        audio = audio.squeeze()
        audio = audio.cpu().numpy()
        audio = audio.astype('int16')
    
    return audio, hparams.sampling_rate

import sounddevice as sd
from sty import fg, bg, ef, rs
from flask import Flask

app = Flask(__name__)
@app.route('/')

def dadbot():

    def webprint(text):
         print(text, flush=True)
         return ('/')

    print("¡Da-bot está listo para cascar! Escribe tus mensajes o dile 'quieto parao'")
    while True:
        a = input()
      
        if a == 'quieto parao':
            break
        responses = agent.handle_text(a)
        for response in responses:
            to_synth = response["text"]
            #to_synth = "Esto es una prueba para ver si funciona"
            webprint(fg.yellow + to_synth + fg.rs)
            response_file = open('response.txt','w') 
            response_file.write(to_synth)
            voice, sr = synthesize(to_synth, "orador")
            sd.play(voice, sr)
            response_file.close()
    return []

