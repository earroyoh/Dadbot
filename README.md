# Dadbot

## python virtual environment and pip dependencies
python3 -m venv rasa\
source ~/rasa/bin/activate\
python3 -m pip install --upgrade pip\
python3 -m pip install -r requirements.txt\
python3 -m pip install -r requirements-web.txt\
python3 -m pip install -r actions/requirements-actions.txt

## If using NVIDIA models, modules for speech synthesis
cd ..\
git clone https://github.com/NVIDIA/apex.git \
git clone https://github.com/NVIDIA/DeepLearningExamples.git \
cd Dadbot\
ln -s ../DeepLearningExamples/CUDA-Optimized/FastSpeech/fastspeech fastspeech\
ln -s ../DeepLearningExamples/CUDA-Optimized/FastSpeech/tacotron2 tacotron2\
ln -s ../DeepLearningExamples/CUDA-Optimized/FastSpeech/waveglow waveglow\
ln -s ../waveglow tacotron2/waveglow

## Start rasa server
rasa train\
rasa shell --debug

## Start actions and API server
rasa run actions --debug\
rasa run -m models --enable-api --cors 'https://dadbot-web.ddns.net:8000' --connector voice_connector.ChatInput --debug

#### or as docker deployment

docker build -t dadbot-actions:1.0 -f Dockerfile_actions . \
docker build -t dadbot-web:1.0 -f Dockerfile_web . \
docker build -t dadbot-api:1.0 -f Dockerfile_api .

docker network create frontend-net

docker run -d -p 5005:5005 --name dadbot-connector -v /home/debian/workspace/Dadbot/models:/app/models --hostname dadbot-connector.ddns.net --network frontend-net -e RASA_TELEMETRY_ENABLED=false dadbot-api:1.0

docker run -d -p 5055:5055 --name dadbot-actions --hostname dadbot-actions --network frontend-net -e RASA_TELEMETRY_ENABLED=false -e OPENAI_AI_KEY=\<YOUR OPENAI_API_KEY\> dadbot-actions:1.0

docker run -d -p 0.0.0.0:8000:8000 --name dadbot-web.ddns.net --hostname dadbot-web.ddns.net --network frontend-net dadbot-web:1.0

#### If using NVIDIA models, docker nvidia runtime as default required (include in /etc/docker/daemon.json) and also nvcr.io registry development login
docker build -t dadbot-api:1.0 -f Dockerfile_cuda .

## Terraform docker provider
cd terraform/docker\
export TF_VAR_OPENAI_API_KEY=\<YOUR OPENAI_API_KEY\>\
terraform init\
terraform apply

## Train the bot as i.e. jupyter notebook (include your own domain.yml file) 
sudo ./gen_webserver_cert.sh \<URL\> \<IP\>\
jupyter notebook --ip=0.0.0.0 --certfile=dadbot.crt --keyfile=dadbot.key dadbot.ipynb

## Start bot as Sanic app (domain already trained)

#### Self-signed certificates just for testing, e.g. dadbot-web.ddns.net (include your own certificates for production)
sudo ./gen_webserver_cert.sh \<URL\> \<IP\>

python3 dadbot.py

## Start bot as Django app (domain already trained)
python3 manage.py runserver
