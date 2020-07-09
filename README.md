# Dadbot

## Conda environment dependencies
curl --insecure -o miniconda3.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh | bash\
export PATH=$HOME/miniconda3/bin:$PATH
conda init --all
conda create -n rasa\
conda activate rasa\
conda install --file conda_package_spec.txt\
curl -L0 https://bootstrap.pypa.io/get-pip.py | python3\
pip3 install -r requirements

## NVIDIA modules for speech synthesis
git clone https://github.com/NVIDIA/tacotron2.git \
cd tacotron2\
git submodule init; git submodule update\
cd ..\
git clone https://github.com/NVIDIA/apex

## Start actions server
python -m rasa_core_sdk.endpoint --debug --actions actions &

## Train the bot as jupyter notebook (include your own domain.yml file) 
./gen_webserver_cert.sh\
jupyter notebook --ip=0.0.0.0 --certfile=dadbot.crt --keyfile=dadbot.key dadbot.ipynb

## Start bot as flask app (domain already trained)
./gen_webserver_cert.sh\
export FLASK_APP=dadbot.py\
python -m flask run --host=0.0.0.0 --cert=dadbot.crt --key=dadbot.key
