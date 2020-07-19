FROM python:3.7-slim as builder

# To install system dependencies
RUN apt-get update -qq && \
    apt-get install -y git gcc curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

FROM builder as runner

# Conda and pip dependencies
USER 1001
WORKDIR /app
RUN git init && \
    git clone https://github.com/earroyoh/Dadbot.git
WORKDIR /app/Dadbot
RUN pip install --no-cache-dir --user -r requirements.txt

## NVIDIA modules for speech synthesis
RUN git clone https://github.com/NVIDIA/tacotron2.git && \
    cd tacotron2 && \
    git submodule init; git submodule update && \
    ln -s waveglow/denoiser.py denoiser.py && \
    cd .. && \
    git clone https://github.com/NVIDIA/apex

ENV FLASK_APP=dadbot.py; PYTHONPATH=/app/Dadbot:/app/Dadbot/tacotron2:/app/Dadbot/tacotron2/waveglow
EXPOSE 5000
CMD ["python3", "-m", "flask", "run"]
