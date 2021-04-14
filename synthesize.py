import os
import asyncio

#os.system("git clone https://github.com/NVIDIA/tacotron2.git")
#os.system("git clone https://github.com/NVIDIA/apex.git")
#os.system("cd tacotron2; git submodule init; git submodule update")
#os.system("git clone https://github.com/NVIDIA/DeepLearningExamples.git")
#os.system("ln -s DeepLearningExamples/CUDA-Optimized/FastSpeech/fastspeech fastspeech")

from tacotron2.hparams import create_hparams
from tacotron2.model import Tacotron2
from tacotron2.stft import STFT
from tacotron2.audio_processing import griffin_lim
from tacotron2.train import load_model
from fastspeech.text_norm import text_to_sequence
from fastspeech.inferencer.denoiser import Denoiser
from fastspeech.inferencer.inferencer import Inferencer
import numpy as np
import torch

def synthesize(text, voice, sigma=0.6, denoiser_strength=0.1, is_fp16=False):

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
    waveglow = torch.load(waveglow_path, map_location='cuda')['model']
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
        audio = audio * hparams.max_wav_value
        audio = audio.squeeze()
        audio = audio.cpu().numpy()
        audio = audio.astype('int16')

    return audio, hparams.sampling_rate


async def play_buffer(buffer, samplerate):
    loop = asyncio.get_event_loop()
    event = asyncio.Event()
    idx = 0

    def callback(outdata, frame_count, time_info, status):
        nonlocal idx
        if status:
            print(status)
        remainder = len(buffer) - idx
        if remainder == 0:
            loop.call_soon_threadsafe(event.set)
            raise sd.CallbackStop
        valid_frames = frame_count if remainder >= frame_count else remainder
        outdata[:valid_frames] = buffer[idx:idx + valid_frames]
        outdata[valid_frames:] = 0
        idx += valid_frames

    stream = sd.OutputStream(callback=callback, dtype=buffer.dtype,
                    channels=buffer.shape[1], samplerate=samplerate)
    with stream:
        await event.wait()

