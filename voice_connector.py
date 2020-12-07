import asyncio
import inspect
import json
import logging
from asyncio import Queue, CancelledError
from sanic import Sanic, Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from typing import Text, Dict, Any, Optional, Callable, Awaitable, NoReturn

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
from tacotron2.waveglow.mel2samp import files_to_list, MAX_WAV_VALUE
from fastspeech.inferencer.denoiser import Denoiser
import numpy as np
import torch
import sounddevice as sd

logger = logging.getLogger(__name__)

def synthesize(text, voice, sigma=0.6, denoiser_strength=0.08, is_fp16=False):

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
    waveglow = torch.load(waveglow_path)['model']
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
        audio = audio * MAX_WAV_VALUE
        audio = audio.squeeze()
        audio = audio.cpu().numpy()
        audio = audio.astype('int16')

    return audio, hparams.sampling_rate

async def play_buffer(buffer, samplerate):
    loop = asyncio.get_event_loop()
    event = asyncio.Event()
    idx = 0

    def callback(outdata, frame_count, time_info, status):
        nonlocal idx
        if status:
            print(status)
        remainder = len(buffer) - idx
        if remainder == 0:
            loop.call_soon_threadsafe(event.set)
            raise sd.CallbackStop
        valid_frames = frame_count if remainder >= frame_count else remainder
        outdata[:valid_frames] = buffer[idx:idx + valid_frames]
        outdata[valid_frames:] = 0
        idx += valid_frames

    stream = sd.OutputStream(callback=callback, dtype=buffer.dtype,
                    channels=buffer.shape[1], samplerate=samplerate)
    with stream:
        await event.wait()


class ChatInput(InputChannel):
    """A custom http input channel.

    This implementation is the basis for a custom implementation of a chat
    frontend. You can customize this to send messages to Rasa and
    retrieve responses from the assistant."""

    @classmethod
    def name(cls) -> Text:
        return "voice"

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
                for botutterances in collector.messages:
                    botutterance = botutterances["text"]
                    logger.error(f"BotUttered message '{botutterance}'.")
                    voice, sr = synthesize(botutterance, "constantino")

                    #Stream bot voice through HTTP server
                    stream = sd.OutputStream(dtype='int16', channels=1, samplerate=22050.0)
                    stream.start()
                    stream.write(voice)
                    stream.close()
                    #sd.play(voice, sr)

                return response.json(collector.messages)

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

