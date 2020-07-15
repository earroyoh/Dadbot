FROM python:3.7-slim as builder

# To install system dependencies
RUN apt-get update -qq && \
    apt-get install -y git gcc curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN curl --insecure -o miniconda3.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash miniconda3.sh -b -p /app/miniconda3
ENV PATH=/app/miniconda3/bin:$PATH
RUN conda install --update-deps -y conda=4.7.12 && \
    conda clean --all --yes
RUN chgrp -R 0 /app && chmod -R g=u /app
RUN conda install --file conda_package_spec.txt && \
    conda clean --all --yes
RUN pip install --no-cache-dir -r requirements.txt

FROM builder as runner

# Conda and pip dependencies
WORKDIR /app
RUN git init && \
    git clone https://github.com/earroyoh/Dadbot.git

## NVIDIA modules for speech synthesis
WORKDIR /app/Dadbot
RUN git clone https://github.com/NVIDIA/tacotron2.git && \
    cd tacotron2 && \
    git submodule init; git submodule update && \
    cd .. && \
    git clone https://github.com/NVIDIA/apex

ENV FLASK_APP=dadbot.py; PYTHONPATH=/app/Dadbot:/app/Dadbot/tacotron2:/app/Dadbot/tacotron2/waveglow
EXPOSE 5000
CMD ["python3", "-m", "flask", "run"]
