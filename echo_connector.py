import asyncio
import inspect
import json
import logging
import os
import time
from asyncio import Queue, CancelledError
from sanic import Sanic, Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from typing import Text, Dict, Any, Optional, Callable, Awaitable, NoReturn
import requests

import rasa.utils.endpoints
from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)

from tacotron2.hparams import create_hparams
from tacotron2.model import Tacotron2
from tacotron2.stft import STFT
from tacotron2.audio_processing import griffin_lim
from tacotron2.train import load_model
from fastspeech.text_norm import text_to_sequence
from fastspeech.inferencer.denoiser import Denoiser
from fastspeech.inferencer.inferencer import Inferencer
import numpy as np
import torch
import sounddevice as sd
from scipy.io.wavfile import write

logger = logging.getLogger(__name__)

def synthesize(text, voice, sigma=0.6, denoiser_strength=0.1, is_fp16=False):

    hparams = create_hparams()
    hparams.sampling_rate = 22050

    if voice == "papaito":
        voice_model = "nvidia_tacotron2_papaito_300"
    elif voice == "constantino":
        voice_model = "tacotron2_Constantino_600"
    elif voice == "orador":
        voice_model = "checkpoint_tacotron2_29000_es"
   
    checkpoint_path = "/home/debian/workspace/models/" + voice_model

    model = load_model(hparams)
    model.load_state_dict(torch.load(checkpoint_path)['state_dict'])
    _ = model.cuda().eval().half()

    waveglow_path = '/home/debian/workspace/models/waveglow_256channels_ljs_v2.pt'
    waveglow = torch.load(waveglow_path, map_location='cuda')['model']
    _ = waveglow.cuda().eval().half()
    denoiser = Denoiser(waveglow)

    #text="¡Cágate lorito!"
    #with open(filelist_path, encoding='utf-8', mode='r') as f:
    #    text = f.read()

    sequence = np.array(text_to_sequence(text, ['english_cleaners']))[None, :]
    sequence = torch.autograd.Variable(
        torch.from_numpy(sequence)).cuda().long()

    mel_outputs, mel_outputs_postnet, _, alignments = model.inference(sequence)
    #mel = torch.unsqueeze(mel, 0)
    mel = mel_outputs.half() if is_fp16 else mel_outputs
    audio = np.array([])
    with torch.no_grad():
        audio = waveglow.infer(mel, sigma=sigma)
        if denoiser_strength > 0:
             audio = denoiser(audio, denoiser_strength)
        audio = audio * hparams.max_wav_value
        audio = audio.squeeze()
        audio = audio.cpu().numpy()
        audio = audio.astype('int16')

    return audio, hparams.sampling_rate


class ChatInput(InputChannel):
    """A custom http input channel.

    This implementation is the basis for a custom implementation of a chat
    frontend. You can customize this to send messages to Rasa and
    retrieve responses from the assistant."""

    @classmethod
    def name(cls) -> Text:
        return "voice"

    @classmethod
    def from_credentials(cls, credentials):
        credentials = credentials or {}
        return cls(credentials.get("speaker", "constantino"),
                   credentials.get("sigma", 0.6),
                   credentials.get("denoiser", 0.1),
                   credentials.get("stream", False),
                   )

    def __init__(self,
                 speaker: Text = "constantino",
                 sigma: Optional[float] = 0.6,
                 denoiser: Optional[float] = 0.1,
                 should_use_stream: bool = False,
                 ):
        self.speaker = speaker
        self.sigma = sigma
        self.denoiser = denoiser
        self.should_use_stream = should_use_stream

    @staticmethod
    async def on_message_wrapper(
        on_new_message: Callable[[UserMessage], Awaitable[Any]],
        text: Text,
        queue: Queue,
        sender_id: Text,
        input_channel: Text,
        metadata: Optional[Dict[Text, Any]],
    ) -> None:
        collector = QueueOutputChannel(queue)

        message = UserMessage(
            text, collector, sender_id, input_channel=input_channel, metadata=metadata
        )
        await on_new_message(message)

        await queue.put("DONE")

    async def _extract_sender(self, req: Request) -> Optional[Text]:
        return req.json.get("sender", None)

    # noinspection PyMethodMayBeStatic
    def _extract_message(self, req: Request) -> Optional[Text]:
        return req.json.get("message", None)

    def _extract_input_channel(self, req: Request) -> Text:
        return req.json.get("input_channel") or self.name()

    def stream_response(
        self,
        on_new_message: Callable[[UserMessage], Awaitable[None]],
        text: Text,
        sender_id: Text,
        input_channel: Text,
        metadata: Optional[Dict[Text, Any]],
    ) -> Callable[[Any], Awaitable[None]]:
        async def stream(resp: Any) -> None:
            q = Queue()
            task = asyncio.ensure_future(
                self.on_message_wrapper(
                    on_new_message, text, q, sender_id, input_channel, metadata
                )
            )
            while True:
                result = await q.get()
                if result == "DONE":
                    break
                else:
                    await resp.write(json.dumps(result) + "\n")
            await task

        return stream

    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:
        custom_webhook = Blueprint(
            "custom_webhook_{}".format(type(self).__name__),
            inspect.getmodule(self).__name__,
        )

        # noinspection PyUnusedLocal
        @custom_webhook.route("/", methods=["GET"])
        async def health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @custom_webhook.route("/webhook", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            sender_id = await self._extract_sender(request)
            text = self._extract_message(request)
            should_use_stream = rasa.utils.endpoints.bool_arg(
                request, "stream", default=False
            )
            input_channel = self._extract_input_channel(request)
            metadata = self.get_metadata(request)

            if should_use_stream:
                return response.stream(
                    self.stream_response(
                        on_new_message, text, sender_id, input_channel, metadata
                    ),
                    content_type="text/event-stream",
                )
            else:
                collector = CollectingOutputChannel()
                # noinspection PyBroadException
                try:

                    # Synthesize bot voice with desired pretrained NVIDIA Tacotron2 spanish fine-tuned voice model
                    botutterance = text
                    logger.debug(f"BotUttered message '{botutterance}'.")
                    voice, sr = synthesize(botutterance, self.speaker, self.sigma, self.denoiser)

                    #Stream bot voice through HTTP server
                    #stream = sd.OutputStream(dtype='int16', channels=1, samplerate=22050.0)
                    #stream.start()
                    #stream.write(voice)
                    #stream.close()
                    #sd.play(voice, sr)

                    audio_file = "0_{}_synthesis.wav".format(sender_id)
                    audio_path = os.path.join(
                        "./rasadjango/dadbot/audios/", audio_file)
                    write(audio_path, sr, voice)
                    #url = "http://192.168.1.103:8000/audios/{}_".format(i) + "{}".format(sender_id)
                    url = "http://2d13b4160f7d.eu.ngrok.io/audios/0_{}".format(sender_id)
                    with open(audio_path, 'rb') as f:
                        files = {"files": (audio_path, f, 'application/octet-stream')}
                        requests.post(url, files = files)
                        f.close()

                except CancelledError:
                    logger.error(
                        f"Message handling timed out for " f"user message '{text}'."
                    )
                except Exception:
                    logger.exception(
                        f"An exception occured while handling "
                        f"user message '{text}'."
                    )

                #return response.json(collector.messages)
                return response.json([{"text": botutterance}])

        return custom_webhook


class QueueOutputChannel(CollectingOutputChannel):
    """Output channel that collects send messages in a list

    (doesn't send them anywhere, just collects them)."""

    @classmethod
    def name(cls) -> Text:
        return "queue"

    # noinspection PyMissingConstructor
    def __init__(self, message_queue: Optional[Queue] = None) -> None:
        super().__init__()
        self.messages = Queue() if not message_queue else message_queue

    def latest_output(self) -> NoReturn:
        raise NotImplementedError("A queue doesn't allow to peek at messages.")

    async def _persist_message(self, message) -> None:
        await self.messages.put(message)

