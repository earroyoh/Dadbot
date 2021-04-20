import os
from scipy.io.wavfile import write
import torch
from tensorboard.plugins.hparams import api as hp
import tensorflow as tf

import sys
sys.path.append('tacotron2/waveglow/')
import numpy as np

from tacotron2.hparams import create_hparams
from tacotron2.model import Tacotron2
from tacotron2.stft import STFT
from tacotron2.audio_processing import griffin_lim
from tacotron2.train import load_model
from tacotron2.mel2samp import files_to_list, MAX_WAV_VALUE
from fastspeech.inferencer.denoiser import Denoiser
from fastspeech.text_norm import text_to_sequence
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', "--filelist_path", required=True)
#parser.add_argument('-f', "--filelist_path")
parser.add_argument('-c', '--checkpoint_path',
                    help='Path to tacotron2 spectrogram encoder checkpoint with model')
parser.add_argument('-w', '--waveglow_path',
                    help='Path to waveglow decoder checkpoint with model')
parser.add_argument('-o', "--output_dir", required=True)
parser.add_argument("-s", "--sigma", default=1.0, type=float)
parser.add_argument("--sampling_rate", default=22050, type=int)
parser.add_argument("--is_fp16", action="store_true")
parser.add_argument("-d", "--denoiser_strength", default=0.0, type=float,
                    help='Removes model bias. Start with 0.1 and adjust')

args = parser.parse_args()

hparams = []
hparams = create_hparams()
#hparams[HP_SAMPLING_RATE] = 22050

#checkpoint_path = "output/checkpoint_29000"
checkpoint_path = args.checkpoint_path
model = load_model(hparams)
model.load_state_dict(torch.load(checkpoint_path)['state_dict'])
_ = model.cuda().eval().half()

#waveglow_path = '/media/debian/SSD_USB/models/waveglow_256channels_ljs_v2.pt'
waveglow = torch.load(args.waveglow_path)['model']
_ = waveglow.cuda().eval().half()
denoiser = Denoiser(waveglow)

#text="¡Cágate lorito!"
with open(args.filelist_path, encoding='utf-8', mode='r') as f:
	text = f.read()

sequence = np.array(text_to_sequence(text, ['english_cleaners']))[None, :]
sequence = torch.autograd.Variable(
    torch.from_numpy(sequence)).cuda().long()

mel_outputs, mel_outputs_postnet, _, alignments = model.inference(sequence)
#mel = torch.unsqueeze(mel, 0)
mel = mel_outputs.half() if args.is_fp16 else mel_outputs
with torch.no_grad():
    audio = waveglow.infer(mel, sigma=args.sigma)
    if args.denoiser_strength > 0:
         audio = denoiser(audio, args.denoiser_strength)
    audio = audio * MAX_WAV_VALUE
    audio = audio.squeeze()
    audio = audio.cpu().numpy()
    audio = audio.astype('int16')
    file_name = "audio"
    audio_path = os.path.join(
        args.output_dir, "{}_synthesis.wav".format(file_name))
    write(audio_path, args.sampling_rate, audio)
    print(audio_path)
