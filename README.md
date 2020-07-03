# Dadbot

## Conda environment dependencies
curl --insecure https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh | bash\
conda create -n rasa\
conda activate rasa\
conda install --file conda_package_spec.txt

## NVIDIA modules for speech synthesis
git clone https://github.com/NVIDIA/tacotron2.git \
cd tacotron2\
git subomdule init; git submodule update\
cd ..\
git clone https://github.com/NVIDIA/apex

## Start bot as flask app
export FLASK_APP=dadbot.py\
python -m flask run
