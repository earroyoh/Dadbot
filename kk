#1 [internal] load build definition from Dockerfile_speaker
#1 sha256:45c8fae1896c25acaaaf156f775046dac2558b9fed6e4c19d2ea34fb86150d42
#1 transferring dockerfile: 1.33kB done
#1 DONE 0.1s

#2 [internal] load .dockerignore
#2 sha256:d1a600dac4e933a5d453721091d9fd491d35dc222c0fa1afe688e4a92d478fa7
#2 transferring context: 2B done
#2 DONE 0.0s

#3 [internal] load metadata for docker.io/library/python:3.9-slim
#3 sha256:3425157df499c84dd49181e5611a11caeed16adf15a5ddbcfa4c3002c56d3d27
#3 DONE 1.4s

#4 [ 1/14] FROM docker.io/library/python:3.9-slim@sha256:8434c99df85cc274108beac4465d4abbc4459956bb2b7a84073636ac5f4b7c1a
#4 sha256:a5d15a4b5e65769dd5c0b0541149f9cb8c0838d8c5e4cd5afdca81501e8afa87
#4 resolve docker.io/library/python:3.9-slim@sha256:8434c99df85cc274108beac4465d4abbc4459956bb2b7a84073636ac5f4b7c1a 0.0s done
#4 DONE 0.0s

#8 [internal] load build context
#8 sha256:3e2d0fbae0c4c06a6bc83cce2c6b060db8ae218132505a8133ae6caba0b305ab
#8 transferring context: 13.40kB done
#8 DONE 0.1s

#5 [ 2/14] RUN apt-get -y -qq update && apt-get -y -qq install --no-install-recommends gcc python3-soundfile libsndfile1 portaudio19-dev python3-glob2 ffmpeg &&     apt-get -qq -y autoremove &&     apt-get autoclean &&     rm -rf /var/lib/apt/lists/*
#5 sha256:c49073d206613edbf9fd63b9571a38e18b7d6d7ab0250de69d12ba4c48fec76d
#5 CACHED

#6 [ 3/14] RUN groupadd -g 1000 -r debian &&   useradd -u 1000 -r -g debian -m -d /home/debian debian
#6 sha256:b623c067184a9335b6954ce9c57b9f307e56f898466b3f14297d7e4caf2138ae
#6 CACHED

#7 [ 4/14] WORKDIR /app
#7 sha256:72e45dce14e03841e05c6219d927f93d29ed11a716c50309cbe82ed0fed8b5a6
#7 CACHED

#9 [ 5/14] COPY speaker.py /app/speaker.py
#9 sha256:30c3a433428ab430ed6a013a53928874139ee21f64d68009ed78709920fca508
#9 DONE 0.5s

#10 [ 6/14] COPY sileroSTT.py /app/sileroSTT.py
#10 sha256:8ae53a05cf298ee3d71fc847e312ec477b23f7031e3d29fe51a8f909aa73f332
#10 DONE 0.1s

#11 [ 7/14] COPY sileroTTS.py /app/sileroTTS.py
#11 sha256:aebc7151ac7d80701933dfad5c5b9359c3d5b8627b3c53aebb2d25b208a107a1
#11 DONE 0.1s

#12 [ 8/14] COPY synthesize.py /app/synthesize.py
#12 sha256:2b47b21d3e82821d7ceb563a252e34c0e0b563a48c63d69202acdc8e9d2d378a
#12 DONE 0.1s

#13 [ 9/14] COPY requirements-speaker.txt /app/requirements-speaker.txt
#13 sha256:9c8aa08398c6f6f06b6f4cdf372eac04c9c170e4b4bbf399b53d80d56f039486
#13 DONE 0.1s

#14 [10/14] COPY dadbot.crt /app/dadbot.crt
#14 sha256:64a6069acc1a1b6014e4715efd90820f002a5655bb01c2621c38dab0e2c5b22b
#14 DONE 0.1s

#15 [11/14] COPY dadbot.key /app/dadbot.key
#15 sha256:323eb38e398509c8951c40afbf5d636fc1e753531a56e7779b475923ce18f170
#15 DONE 0.1s

#16 [12/14] RUN chgrp -R 1000 /app && chmod -R g=u /app
#16 sha256:8c53b9c25fcce2b55edfec8a6a5dfcde451413b54e5c339bf95656dfee0ef958
#16 DONE 0.6s

#17 [13/14] RUN python3 -m pip install -t /app/.local --upgrade pip &&     python3 -m pip install -t /app/.local --upgrade --no-cache-dir -r requirements-speaker.txt
#17 sha256:9ebbf8529106179a8c087d6a7a62dcd05abfd44ad0c4e5b6f110563c95846e11
#17 5.502 Collecting pip
#17 5.621   Downloading pip-21.2.4-py3-none-any.whl (1.6 MB)
#17 6.370 Installing collected packages: pip
#17 8.306 Successfully installed pip-21.2.4
#17 11.36 Collecting sanic==19.12.2
#17 11.45   Downloading sanic-19.12.2-py3-none-any.whl (72 kB)
#17 11.59 Collecting sanic_cors==0.10.0.post3
#17 11.61   Downloading Sanic_Cors-0.10.0.post3-py2.py3-none-any.whl (17 kB)
#17 11.68 Collecting unidecode
#17 11.69   Downloading Unidecode-1.3.2-py3-none-any.whl (235 kB)
#17 11.80 Collecting jinja2
#17 11.81   Downloading Jinja2-3.0.1-py3-none-any.whl (133 kB)
#17 12.09 Collecting torch
#17 12.12   Downloading torch-1.9.1-cp39-cp39-manylinux1_x86_64.whl (831.4 MB)
#17 106.0 Collecting torchaudio
#17 106.3   Downloading torchaudio-0.9.1-cp39-cp39-manylinux1_x86_64.whl (1.9 MB)
#17 106.7 Collecting sounddevice
#17 106.8   Downloading sounddevice-0.4.2-py3-none-any.whl (31 kB)
#17 106.9 Collecting soundfile
#17 106.9   Downloading SoundFile-0.10.3.post1-py2.py3-none-any.whl (21 kB)
#17 107.0 Collecting sty
#17 107.0   Downloading sty-1.0.0rc2-py3-none-any.whl (11 kB)
#17 107.1 Collecting inflect
#17 107.2   Downloading inflect-5.3.0-py3-none-any.whl (32 kB)
#17 107.4 Collecting omegaconf
#17 107.4   Downloading omegaconf-2.1.1-py3-none-any.whl (74 kB)
#17 107.9 Collecting scipy
#17 107.9   Downloading scipy-1.7.1-cp39-cp39-manylinux_2_5_x86_64.manylinux1_x86_64.whl (28.5 MB)
#17 111.4 Collecting uvloop>=0.5.3
#17 111.4   Downloading uvloop-0.16.0-cp39-cp39-manylinux_2_12_x86_64.manylinux2010_x86_64.whl (4.3 MB)
#17 111.9 Collecting aiofiles>=0.3.0
#17 111.9   Downloading aiofiles-0.7.0-py3-none-any.whl (13 kB)
#17 113.3 Collecting multidict<5.0,>=4.0
#17 113.3   Downloading multidict-4.7.6.tar.gz (50 kB)
#17 113.6   Installing build dependencies: started
#17 119.7   Installing build dependencies: finished with status 'done'
#17 119.7   Getting requirements to build wheel: started
#17 120.5   Getting requirements to build wheel: finished with status 'done'
#17 120.5     Preparing wheel metadata: started
#17 121.5     Preparing wheel metadata: finished with status 'done'
#17 121.6 Collecting ujson>=1.35
#17 121.7   Downloading ujson-4.2.0-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (218 kB)
#17 121.9 Collecting websockets<9.0,>=7.0
#17 122.0   Downloading websockets-8.1.tar.gz (58 kB)
#17 123.0 Collecting httptools>=0.0.10
#17 123.1   Downloading httptools-0.3.0-cp39-cp39-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_12_x86_64.manylinux2010_x86_64.whl (428 kB)
#17 123.2 Collecting httpx==0.9.3
#17 123.2   Downloading httpx-0.9.3-py2.py3-none-any.whl (64 kB)
#17 123.3 Collecting sanic-plugins-framework>=0.9.0
#17 123.3   Downloading Sanic_Plugins_Framework-0.9.5-py2.py3-none-any.whl (23 kB)
#17 123.4 Collecting chardet==3.*
#17 123.4   Downloading chardet-3.0.4-py2.py3-none-any.whl (133 kB)
#17 123.5 Collecting h11==0.8.*
#17 123.5   Downloading h11-0.8.1-py2.py3-none-any.whl (55 kB)
#17 123.5 Collecting sniffio==1.*
#17 123.5   Downloading sniffio-1.2.0-py3-none-any.whl (10 kB)
#17 123.6 Collecting idna==2.*
#17 123.6   Downloading idna-2.10-py2.py3-none-any.whl (58 kB)
#17 123.7 Collecting certifi
#17 123.7   Downloading certifi-2021.5.30-py2.py3-none-any.whl (145 kB)
#17 123.8 Collecting h2==3.*
#17 123.8   Downloading h2-3.2.0-py2.py3-none-any.whl (65 kB)
#17 124.0 Collecting hstspreload
#17 124.0   Downloading hstspreload-2021.10.1-py3-none-any.whl (1.2 MB)
#17 124.2 Collecting rfc3986<2,>=1.3
#17 124.2   Downloading rfc3986-1.5.0-py2.py3-none-any.whl (31 kB)
#17 124.3 Collecting hyperframe<6,>=5.2.0
#17 124.4   Downloading hyperframe-5.2.0-py2.py3-none-any.whl (12 kB)
#17 124.4 Collecting hpack<4,>=3.0
#17 124.4   Downloading hpack-3.0.0-py2.py3-none-any.whl (38 kB)
#17 124.7 Collecting MarkupSafe>=2.0
#17 124.7   Downloading MarkupSafe-2.0.1-cp39-cp39-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_12_x86_64.manylinux2010_x86_64.whl (30 kB)
#17 124.8 Collecting typing-extensions
#17 124.8   Downloading typing_extensions-3.10.0.2-py3-none-any.whl (26 kB)
#17 125.5 Collecting CFFI>=1.0
#17 125.5   Downloading cffi-1.14.6-cp39-cp39-manylinux1_x86_64.whl (405 kB)
#17 125.7 Collecting antlr4-python3-runtime==4.8
#17 125.7   Downloading antlr4-python3-runtime-4.8.tar.gz (112 kB)
#17 126.7 Collecting PyYAML>=5.1.0
#17 126.8   Downloading PyYAML-5.4.1-cp39-cp39-manylinux1_x86_64.whl (630 kB)
#17 127.7 Collecting numpy<1.23.0,>=1.16.5
#17 127.7   Downloading numpy-1.21.2-cp39-cp39-manylinux_2_12_x86_64.manylinux2010_x86_64.whl (15.8 MB)
#17 129.3 Collecting pycparser
#17 129.3   Downloading pycparser-2.20-py2.py3-none-any.whl (112 kB)
#17 130.2 Collecting setuptools>=40.0
#17 130.3   Downloading setuptools-58.2.0-py3-none-any.whl (946 kB)
#17 130.6 Building wheels for collected packages: antlr4-python3-runtime, multidict, websockets
#17 130.6   Building wheel for antlr4-python3-runtime (setup.py): started
#17 131.9   Building wheel for antlr4-python3-runtime (setup.py): finished with status 'done'
#17 131.9   Created wheel for antlr4-python3-runtime: filename=antlr4_python3_runtime-4.8-py3-none-any.whl size=141230 sha256=a5a671de9a40f9278970f4346d9d2f5cb057624d3d9fd210201dd4425acc0a8b
#17 131.9   Stored in directory: /tmp/pip-ephem-wheel-cache-33xl7oq3/wheels/42/3c/ae/14db087e6018de74810afe32eb6ac890ef9c68ba19b00db97a
#17 131.9   Building wheel for multidict (PEP 517): started
#17 134.4   Building wheel for multidict (PEP 517): finished with status 'done'
#17 134.4   Created wheel for multidict: filename=multidict-4.7.6-cp39-cp39-linux_x86_64.whl size=50805 sha256=269913770b418e2229a5c3ad4b0753f529140377887abdf51b20d164ae16660e
#17 134.4   Stored in directory: /tmp/pip-ephem-wheel-cache-33xl7oq3/wheels/43/3a/a8/d7bf95ae763a7a2057cb502ff2da094763c166f253624afc63
#17 134.4   Building wheel for websockets (setup.py): started
#17 135.9   Building wheel for websockets (setup.py): finished with status 'done'
#17 135.9   Created wheel for websockets: filename=websockets-8.1-cp39-cp39-linux_x86_64.whl size=65432 sha256=0435a22cd52048f835f264e39f294d4c15dd5480a8465ddb7306a871963a7ffc
#17 135.9   Stored in directory: /tmp/pip-ephem-wheel-cache-33xl7oq3/wheels/d8/b9/a0/b97b211aeda2ebd6ac2e43fc300d308dbf1f9df520ed390cae
#17 135.9 Successfully built antlr4-python3-runtime multidict websockets
#17 136.4 Installing collected packages: hyperframe, hpack, sniffio, rfc3986, idna, hstspreload, h2, h11, chardet, certifi, websockets, uvloop, ujson, multidict, httpx, httptools, aiofiles, typing-extensions, setuptools, sanic, pycparser, torch, sanic-plugins-framework, PyYAML, numpy, MarkupSafe, CFFI, antlr4-python3-runtime, unidecode, torchaudio, sty, soundfile, sounddevice, scipy, sanic-cors, omegaconf, jinja2, inflect
#17 162.9 Successfully installed CFFI-1.14.6 MarkupSafe-2.0.1 PyYAML-5.4.1 aiofiles-0.7.0 antlr4-python3-runtime-4.8 certifi-2021.5.30 chardet-3.0.4 h11-0.8.1 h2-3.2.0 hpack-3.0.0 hstspreload-2021.10.1 httptools-0.3.0 httpx-0.9.3 hyperframe-5.2.0 idna-2.10 inflect-5.3.0 jinja2-3.0.1 multidict-4.7.6 numpy-1.21.2 omegaconf-2.1.1 pycparser-2.20 rfc3986-1.5.0 sanic-19.12.2 sanic-cors-0.10.0.post3 sanic-plugins-framework-0.9.5 scipy-1.7.1 setuptools-58.2.0 sniffio-1.2.0 sounddevice-0.4.2 soundfile-0.10.3.post1 sty-1.0.0rc2 torch-1.9.1 torchaudio-0.9.1 typing-extensions-3.10.0.2 ujson-4.2.0 unidecode-1.3.2 uvloop-0.16.0 websockets-8.1
#17 DONE 167.1s

#18 [14/14] RUN mkdir -p /app/rasadjango/dadbot/audios
#18 sha256:9624c129da243de8d795bd146154f90ec8a1f93ed718a14d42ba2a5b7f5fe275
#18 DONE 0.9s

#19 exporting to image
#19 sha256:e8c613e07b0b7ff33893b694f7759a10d42e180f2b4dc349fb57dc6b71dcab00
#19 exporting layers
#19 exporting layers 13.3s done
#19 writing image sha256:bfcf3a4f60644bf4d22b0d51439608805ea8f4a9375a42079eb8d762e7550bea done
#19 naming to docker.io/library/dadbot-speaker:1.0 done
#19 DONE 13.3s
