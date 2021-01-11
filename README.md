# Dadbot

## python virtual environment and pip dependencies
python3 -m venv rasa\
source ~/rasa/bin/activate\
python3 -m pip install --upgrade pip\
python3 -m pip install -r requirements.txt

## NVIDIA modules for speech synthesis
cd ..\
git clone https://github.com/NVIDIA/apex.git \
git clone https://github.com/NVIDIA/DeepLearningExamples.git \
cd Dadbot
ln -s ../DeepLearningExamples/CUDA-Optimized/FastSpeech/fastspeech fastspeech\
ln -s ../DeepLearningExamples/CUDA-Optimized/FastSpeech/tacotron2 tacotron2\
ln -s ../DeepLearningExamples/CUDA-Optimized/FastSpeech/waveglow waveglow\
ln -s ../waveglow tacotron2/waveglow

## Start rasa server
rasa train\
rasa shell --debug

## Start actions and API server
rasa run actions --debug\
rasa run -m models --enable-api --cors '*' --connector voice_connector.ChatInput --debug\

or as docker deployment

docker build -t dadbot-actions:1.0 -f Dockerfile_actions . \
docker build -t dadbot-web:1.0 -f Dockerfile_web . \
### docker nvidia runtime as default required (include in daemon.json)
### and also nvcr.io registry development login
docker build -t dadbot-api:1.0 -f Dockerfile_cuda . \

cd terraform/docker\
terraform init\
terraform apply

## Train the bot as jupyter notebook (include your own domain.yml file) 
./gen_webserver_cert.sh\
jupyter notebook --ip=0.0.0.0 --certfile=dadbot.crt --keyfile=dadbot.key dadbot.ipynb

## Start bot as Sanic app (domain already trained)
./gen_webserver_cert.sh\
python3 dadbot.py

## Start bot as Django app (domain already trained)
python3 manage.py runserver
