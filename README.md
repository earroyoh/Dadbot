# Dadbot

## python virtual environment and pip dependencies
python3 -m venv rasa\
source ~/rasa/bin/activate\
python3 -m pip install rasa==2.1.2

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

## Start bot as Sanic app (domain already trained)
./gen_webserver_cert.sh\
python3 dadbot.py

## Start bot as Django app (domain already trained)
python3 manage.py runserver
