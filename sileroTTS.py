import os
import torch
from omegaconf import OmegaConf
from scipy.io.wavfile import write
import numpy as np

# First time download
#torch.hub.download_url_to_file('https://raw.githubusercontent.com/snakers4/silero-models/master/models.yml',
#                               'latest_silero_models.yml',
#                               progress=False)
#models = OmegaConf.load('latest_silero_models.yml')

language = 'es'
speaker = 'tux_16khz'
device = torch.device('cpu')

def sileroTTS(text):
    model, symbols, sample_rate, example_text, apply_tts = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                                                      model='silero_tts',
                                                                      language=language,
                                                                      speaker=speaker)
                                                                      #force_reload=True)
    model = model.to(device)  # gpu or cpu
    audio = apply_tts(texts=[text],
               model=model,
               sample_rate=sample_rate,
               symbols=symbols,
               device=device)

    for example in audio:
        return np.array(example), 16000
