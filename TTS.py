import os
import torch
from omegaconf import OmegaConf
from scipy.io.wavfile import write
import numpy as np

#torch.hub.download_url_to_file('https://raw.githubusercontent.com/snakers4/silero-models/master/models.yml',
#                               'latest_silero_models.yml',
#                               progress=False)
models = OmegaConf.load('latest_silero_models.yml')


# see latest avaiable models
#available_languages = list(models.tts_models.keys())
#print(f'Available languages {available_languages}')

#for lang in available_languages:
#    speakers = list(models.tts_models.get(lang).keys())
#    print(f'Available speakers for {lang}: {speakers}')

language = 'es'
speaker = 'tux_16khz'
device = torch.device('cpu')
model, symbols, sample_rate, example_text, apply_tts = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                                                      model='silero_tts',
                                                                      language=language,
                                                                      speaker=speaker)
                                                                      #force_reload=True)
model = model.to(device)  # gpu or cpu
audio = apply_tts(texts=["Tres tristes tigres comían trigo en un trigal."],
                  model=model,
                  sample_rate=sample_rate,
                  symbols=symbols,
                  device=device)

file_name = "audio"
output_dir = "."
audio_path = os.path.join(output_dir, "{}_synthesis.wav".format(file_name))
write(audio_path, sample_rate, np.array(audio[0]))
print(audio_path)
