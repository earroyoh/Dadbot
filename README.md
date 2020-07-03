# Dadbot

curl --insecure https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh | bash\
conda create -n rasa\
conda activate rasa\
conda install --file conda_package_spec.txt\
\
git clone https://github.com/NVIDIA/tacotron2.git \
\
export FLASK_APP=dadbot.py\
python -m flask run
