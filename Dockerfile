FROM conda/miniconda3 as builder

# To install system dependencies
RUN apt-get update -qq && \
    apt-get install -y git gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN conda install --update-deps -y conda=4.7.12 && \
    conda clean --all --yes
WORKDIR /app
RUN chgrp -R 0 /app && chmod -R g=u /app

FROM builder as runner

# Conda and pip dependencies
RUN git init && \
    git clone https://github.com/earroyoh/Dadbot.git
WORKDIR /app/Dadbot
RUN conda install --update-deps -y --file conda_package_spec.txt && \
    conda clean --all --yes
RUN pip install --no-cache-dir -r requirements.txt

## NVIDIA modules for speech synthesis
RUN git clone https://github.com/NVIDIA/tacotron2.git && \
    cd tacotron2 && \
    git submodule init; git submodule update && \
    cd .. && \
    git clone https://github.com/NVIDIA/apex && \
    ln -s tacotron2/text text

ENV FLASK_APP=dadbot.py; PYTHONPATH=/app:/app/tacotron2
EXPOSE 5000
CMD ["python3", "-m", "flask", "run"]
