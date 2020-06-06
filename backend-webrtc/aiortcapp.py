import argparse
import asyncio
import json
import logging
import os
import ssl
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from threading import Thread, Timer

import aiohttp_cors
import av
import requests
# import cv2
from aiohttp import web
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
from av import VideoFrame
# from pydub import AudioSegment
from scipy.io.wavfile import write

ROOT = os.path.dirname(__file__)

logger = logging.getLogger("pc")
speakers = set()
speakers_video = set()
listeners = set()
alltracks = set()
pcs = set()
meetings = dict()
buffer = BytesIO()


# def convert_wav_to_ogg(wav_file, filename):
#     return AudioSegment.from_wav(wav_file).export(filename, format="ogg")


def call_external_translator(filename):
    logging.info(f"Calling transcripts with: {filename}")
    # convert_wav_to_ogg(open(filename, "rb"), oggfile)
    requests.post("https://jitsi.web.cern.ch/upload",
                  files={'file': ('helloworld.wav', open(filename, "rb"))})
    dname = os.path.join(os.path.curdir, filename)
    logging.info(f"done, removing: {dname}")


class AudioTransformTrack(MediaStreamTrack):

    kind = "audio"
    codec_name = "pcm_s16le"
    # codec_name = "pcm_s16be"
    # codec_name = "aac"

    def __init__(self, track):
        super().__init__()

        self.track = track
        self._init_container()
        self.now = datetime.now()

    def _init_container(self):
        self.filename = f"test{datetime.now()}.wav"
        self.container = av.open(self.filename, mode="w")
        self.stream = self.container.add_stream(self.codec_name)
        logger.info(f"added {self.track}")

    def send_buffer_to_encoder(self):
        # call_external_translator(self.filename)
        Thread(target=call_external_translator, args=(self.filename, )).start()
        # t.join()

    async def encode_to_container(self, frame):
        if self.container:
            for packet in self.stream.encode(frame):
                self.container.mux(packet)

            diff = datetime.now() - self.now
            if diff > timedelta(seconds=5):
                self.container.close()
                self.container = None
                print("dumping")
                self.send_buffer_to_encoder()
                # print(self.buffer.getbuffer().nbytes)
                self.now = datetime.now()
                self._init_container()

    async def recv(self):
        frame = await self.track.recv()
        # logger.info(f"Got a new frame!!!! {frame}")
        try:
            await self.encode_to_container(frame)
        except Exception as e:
            logging.exception("Exception parsing frame")

        return frame


class VideoTransformTrack(MediaStreamTrack):
    """
    A video stream track that transforms frames from an another track.
    """

    kind = "video"

    def __init__(self, track, transform):
        super().__init__()  # don't forget this!
        self.track = track
        self.transform = transform


async def index(request):
    content = open(os.path.join(ROOT, "backup", "index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def javascript(request):
    content = open(os.path.join(ROOT, "backup", "client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)


async def listener(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)

    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    print(pc_id)
    pcs.add(pc)

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            log_info(f"got message: {message}")
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        log_info("ICE connection state is %s", pc.iceConnectionState)
        if pc.iceConnectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    for speaker in speakers:
        log_info("adding speakers")
        pc.addTrack(speaker)

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)
        if track.kind == "audio":
            pass

        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)

    # handle offer
    await pc.setRemoteDescription(offer)

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    print(pc_id)
    pcs.add(pc)
    # pcs_to_tracks[pc] = []
    # add_tracks_to_pcs()

    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)

    log_info("Created for %s", request.remote)

    # prepare local media
    player = MediaPlayer(os.path.join(ROOT, "demo-instruct.wav"))
    recorder = MediaBlackhole()

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            log_info(f"got message: {message}")
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        log_info("ICE connection state is %s", pc.iceConnectionState)
        if pc.iceConnectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @pc.on("negotiationneeded")
    def on_negotiaion_needed():
        log_info("negotiation needed")

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)

        if track.kind == "audio":
            local_audio = AudioTransformTrack(track)
            speakers.add(local_audio)
            recorder.addTrack(local_audio)
            print("added", local_audio)
        elif track.kind == "video":
            speakers.add(track)
            pc.addTrack(track)

        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)

    # handle offer
    await pc.setRemoteDescription(offer)
    await recorder.start()

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="WebRTC audio / video / data-channels demo"
    )
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host for HTTP server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP server (default: 8080)"
    )
    parser.add_argument("--verbose", "-v", action="count")
    parser.add_argument("--write-audio", help="Write received audio to a file")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(args.cert_file, args.key_file)
    else:
        ssl_context = None

    app = web.Application()
    cors = aiohttp_cors.setup(app)

    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    post_route = app.router.add_post("/offer", offer)
    listener_route = app.router.add_post("/listen", listener)
    cors.add(post_route, {
        "*":
            aiohttp_cors.ResourceOptions(
                expose_headers="*",
                allow_headers="*")
    }
    )
    cors.add(listener_route, {
        "*":
            aiohttp_cors.ResourceOptions(
                expose_headers="*",
                allow_headers="*")
    }
    )

    web.run_app(
        app, access_log=None, host=args.host, port=args.port, ssl_context=ssl_context
    )
