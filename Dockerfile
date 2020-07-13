FROM conda/miniconda3 as builder

# To install system dependencies
USER root
RUN apt-get update -qq && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
WORKDIR /app
RUN chgrp -R 0 /app && chmod -R g=u /app


FROM builder as runner

# Conda and pip dependencies
RUN git init && \
    git clone https://github.com/earroyoh/Dadbot.git
WORKDIR /app/Dadbot
RUN conda install --update-deps -y conda=4.7.12
RUN conda install --update-deps -y --file conda_package_spec.txt && \
    conda clean --all --yes
RUN pip install --no-cache-dir -r requirements.txt

## NVIDIA modules for speech synthesis
RUN git clone https://github.com/NVIDIA/tacotron2.git
RUN cd tacotron2
RUN git submodule init; git submodule update
RUN cd ..
RUN git clone https://github.com/NVIDIA/apex

USER 1001
ENV FLASK_APP=dadbot.py
EXPOSE 5000
CMD ["python3", "-m", "flask", "run"]
