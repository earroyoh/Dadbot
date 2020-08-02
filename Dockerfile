FROM python:3.7-slim as builder

# To install system dependencies
RUN apt-get update -qq && \
    apt-get install -y apt-utils git gcc curl nano && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
WORKDIR /app/Dadbot
COPY . .
RUN rm -Rf WORKDIR /app/Dadbot/tacotron2 2> /dev/null
RUN chown -Rf 1000:1000 /app && \
    chmod -Rf 755 /app

FROM builder as runner

# Conda and pip dependencies
USER 1000
RUN pip install --no-cache-dir -t /app/Dadbot/.local -r requirements.txt

## NVIDIA modules for speech synthesis
RUN git clone https://github.com/NVIDIA/tacotron2.git && \
    cd tacotron2 && \
    git submodule init; git submodule update && \
    ln -s waveglow/denoiser.py denoiser.py && \
    cd .. && \
    git clone https://github.com/NVIDIA/apex

ENV FLASK_APP=dadbot.py; PYTHONPATH=/app/Dadbot/.local:/app/Dadbot/tacotron2:/app/Dadbot/tacotron2/waveglow
EXPOSE 5000
CMD ["python3", "-m", "flask", "run"]
