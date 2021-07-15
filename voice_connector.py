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
from sanic_cors import CORS, cross_origin
from typing import Text, Dict, Any, Optional, Callable, Awaitable, NoReturn
import requests

import rasa.utils.endpoints
from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)

import torch
import sounddevice as sd
from scipy.io.wavfile import write
#from synthesize import synthesize
from sileroSTT import sileroSTT
from sileroTTS import sileroTTS

logger = logging.getLogger(__name__)

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
        return cls(
                   credentials.get("tts", "nvidia"),
                   credentials.get("speaker", "constantino"),
                   credentials.get("sigma", 0.6),
                   credentials.get("denoiser", 0.1),
                   credentials.get("stream", False)
                   )

    def __init__(self,
                 tts: Text = "nvidia",
                 speaker: Text = "constantino",
                 sigma: Optional[float] = 0.6,
                 denoiser: Optional[float] = 0.1,
                 should_use_stream: bool = False
                 ):
        self.tts = tts
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

        #CORS(custom_webhook, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])

        # noinspection PyUnusedLocal
        @custom_webhook.route("/", methods=["GET"])
        async def health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @custom_webhook.route("/webhook", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            sender_id = await self._extract_sender(request)
            text = self._extract_message(request)
	
            
            # Extract user message from recorded voice
            if (text == "--STT--"):
                # Get recorded user voice through HTTP server
                audio_file = "{}_synthesis.wav".format(sender_id)
                audio_path = os.path.join(
                    "./rasadjango/dadbot/audios/", audio_file)

                #url = "https://192.168.1.104:8000/audios/{}".format(audio_file)
                url = "https://dadbot-web.ddns.net:8000/audios/{}".format(audio_file)
                #url = "https://df66bb2ad4a9.eu.ngrok.io/audios/{}".format(audio_file)
                r = requests.get(url, verify=False)

                with open(audio_path, 'wb') as f:
                    f.write(r.content)

                    # Silero STT
                    text = sileroSTT(audio_path)
                    f.close()
                    logger.debug(f"STT result: " + text)
                
                if (text == None):
                    text = "No he entendido lo que me has dicho"

                return response.json({"recipient_id": sender_id, "text": text},
                                     headers={'Access-Control-Allow-Headers': 'x-requested-with'})

            
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
                    await on_new_message(
                        UserMessage(
                            text,
                            collector,
                            sender_id,
                            input_channel=input_channel,
                            metadata=metadata,
                        )
                    )
                except CancelledError:
                    logger.error(
                        f"Message handling timed out for " f"user message '{text}'."
                    )
                except Exception:
                    logger.exception(
                        f"An exception occured while handling "
                        f"user message '{text}'."
                    )

                # Synthesize bot voice with desired pretrained NVIDIA Tacotron2 spanish fine-tuned voice model
                i = 0
                for botutterances in collector.messages:
                    botutterance = botutterances["text"]
                    logger.debug(f"BotUttered message '{botutterance}'.")

                    # Select the TTS model to use via definition in credentials.yml
                    #if (self.tts == "nvidia"):
                    #    voice, sr = synthesize(botutterance, self.speaker, self.sigma, self.denoiser)
                    #else:
                    voice, sr = sileroTTS(botutterance)

                    #Stream bot voice through HTTP server
                    audio_file = "{}_".format(i) + "{}_synthesis.wav".format(sender_id)
                    audio_path = os.path.join(
                        "./rasadjango/dadbot/audios/", audio_file)
                    write(audio_path, sr, voice)
                    #url = "https://192.168.1.104:8000/audios/{}_".format(i) + "{}".format(sender_id)
                    url = "https://dadbot-web.ddns.net:8000/audios/{}_".format(i) + "{}".format(sender_id)
                    #url = "https://df66bb2ad4a9.eu.ngrok.io/audios/{}_".format(i) + "{}".format(sender_id)
                    with open(audio_path, 'rb') as f:
                        files = {"files": (audio_path, f, 'application/octet-stream')}
                        r = requests.post(url, files = files, verify=False)
                        status = r.json()
                        logger.debug(f"File sent #" + str(i) + ": " + json.dumps(status["file_received"]))
                        f.close()
                    i += 1

                return response.json(collector.messages, headers={'Access-Control-Allow-Headers': 'x-requested-with'})

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
