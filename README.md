# Dadbot

## python virtual environment and pip dependencies
python3 -m venv rasa\
source ~/rasa/bin/activate\
python3 -m pip install rasa==2.0.0

## NVIDIA modules for speech synthesis
git clone https://github.com/NVIDIA/tacotron2.git \
cd tacotron2\
git submodule init; git submodule update\
cd ..\
git clone https://github.com/NVIDIA/apex.git \
git clone https://github.com/DeepLearningEnvironments/CUDA-Optimized/FastSpeech.git

## Start actions server
rasa run actions --debug

## Start rasa server
rasa train\
rasa shell --debug

## Train the bot as jupyter notebook (include your own domain.yml file) 
./gen_webserver_cert.sh\
jupyter notebook --ip=0.0.0.0 --certfile=dadbot.crt --keyfile=dadbot.key dadbot.ipynb

## Start bot as flask app (domain already trained)
./gen_webserver_cert.sh\
export FLASK_APP=dadbot.py\
python -m flask run --host=0.0.0.0 --cert=dadbot.crt --key=dadbot.key
