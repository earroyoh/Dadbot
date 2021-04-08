import os
import torch
import zipfile
import torchaudio
from glob import glob
import soundfile as sf

device = torch.device('cpu')  # gpu also works, but our models are fast enough for CPU
model, decoder, utils = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                       model='silero_stt',
                                       language='es', # also available 'de', 'en'
                                       device=device)
(read_batch, split_into_batches,
 read_audio, prepare_model_input) = utils  # see function signature for details

# download a single file, any format compatible with TorchAudio (soundfile backend)
#torch.hub.download_url_to_file('https://opus-codec.org/static/examples/samples/speech_orig.wav',
#                               dst ='speech_orig.wav', progress=True)

def sileroSTT(fname):
    #recorded_files = glob(fname)
    #data, sr = sf.read(recorded_files)
    #sf.write(recorded_files, data, format='wav', samplerate=sr)
    recorded_files = os.path.dirname(fname) + '/transformed_' + os.path.basename(fname)
    # WbeM to WAV required due to MediaStreamRecorder bug (mimeType: 'audio/wav' doesn't work)
    os.system('ffmpeg -v quiet -y -i ' + fname + ' -ar 44100 ' + recorded_files)
    batches = split_into_batches(glob(recorded_files), batch_size=10)
    input = prepare_model_input(read_batch(batches[0]),
                            device=device)

    output = model(input)
    for example in output:
         return decoder(example.cpu())
