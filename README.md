# Dadbot

## Create docker image
docker build -t dadbot:1.0 .

## Start actions server
python -m rasa_sdk.endpoint --debug --actions actions &

## Train the bot as jupyter notebook (include your own domain.yml file) 
./gen_webserver_cert.sh\
jupyter notebook --ip=0.0.0.0 --certfile=dadbot.crt --keyfile=dadbot.key dadbot.ipynb

## Start bot as flask app (domain already trained)
./gen_webserver_cert.sh\
export FLASK_APP=dadbot.py\
python -m flask run --host=0.0.0.0 --cert=dadbot.crt --key=dadbot.key

## Start bot from docker image
docker run -d -t -p 5000:5000 -v $HOME/Dadbot/models:/app/Dadbot/models dadbot:1.0
