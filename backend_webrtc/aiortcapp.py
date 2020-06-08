import argparse
import asyncio
import json
import logging
import os
import ssl
import uuid
import weakref
from datetime import datetime, timedelta
from io import BytesIO
from threading import Thread

import aiohttp
import aiohttp_cors
import av
import requests
from aiohttp import web
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer
from pydub import AudioSegment
from dotenv import load_dotenv


def convert(ogg_file):
    return AudioSegment.from_ogg(ogg_file).export(format="wav", bitrate="16k", parameters=["-ar", "16000"])


def convert_wav_to_ogg(wav_file):
    return AudioSegment.from_wav(wav_file).export(format="ogg")



ROOT = os.path.dirname(__file__)

logger = logging.getLogger("pc")
speakers = dict()
pcs = set()
meetings = dict()
buffer = BytesIO()


# Make sure we have the fresh dotenv
load_dotenv()

# configs
USE_TRANSCRIBER = bool(os.getenv('USE_TRANSCRIBER', "false") == "true")
TRANSLATOR_ENDPOINT = str(os.getenv('TRANSLATOR_ENDPOINT', "http://localhost:5000/upload"))
print(f"USE_TRANSCRIBER: {USE_TRANSCRIBER}")
print(f"TRANSLATOR_ENDPOINT: {TRANSLATOR_ENDPOINT}")

# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8080))


STATIC_PATH = os.path.join(ROOT, "build/static/")

def call_external_translator(ogg_buffer):
    logging.info(f"Calling transcripts dir")
    requests.post(TRANSLATOR_ENDPOINT,
                  files={'file': ('helloworld.ogg', BytesIO(ogg_buffer))})
    logging.info("Submitted transcript")


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
        self.filename = os.path.join(ROOT, f"test{datetime.now()}.wav")
        self.container = av.open(self.filename, mode="w")
        self.stream = self.container.add_stream(self.codec_name)
        logger.info(f"recording on track {self.track}")

    def send_buffer_to_encoder(self):
        # call_external_translator(self.filename)
        # recording_buffer = open(self.filename, "rb").read()
        ogg_buffer = convert_wav_to_ogg(open(self.filename, "rb")).read()
        Thread(target=call_external_translator, args=(ogg_buffer, )).start()
        logging.info(f"done, removing: {self.filename}")
        os.unlink(self.filename)
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
            if USE_TRANSCRIBER:
                await self.encode_to_container(frame)
        except Exception as e:
            logging.exception("Exception parsing frame")

        return frame


async def index(request):
    content = open(os.path.join(ROOT, "build", "index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def listener(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)

    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    pcs.add(pc)

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        log_info("ICE connection state is %s", pc.iceConnectionState)
        if pc.iceConnectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    for speaker, tracks in speakers.items():
        log_info("adding speakers")
        if speaker and speaker.iceConnectionState != "failed":
            for track in tracks:
                pc.addTrack(track)

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)
        if track.kind == "audio":
            pass

        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)

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
    # player = MediaPlayer(os.path.join(ROOT, "demo-instruct.wav"))
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
            speaker_to_remove = speakers.get(pc)
            if speaker_to_remove:
                speakers.pop(pc, None)

    @pc.on("negotiationneeded")
    def on_negotiaion_needed():
        log_info("negotiation needed")

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)
        if pc not in speakers:
            speakers[pc] = set()

        if track.kind == "audio":
            local_audio = AudioTransformTrack(track)
            speakers[pc].add(local_audio)
            recorder.addTrack(local_audio)
        elif track.kind == "video":
            speakers[pc].add(track)
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

    for ws in app['websockets']:
        await ws.close(code=aiohttp.WSCloseCode.GOING_AWAY, message='Server shutdown')


class WebSocket(web.View):
    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        self.request.app['websockets'].add(ws)

        def participant_list(meeting_name):
            meeting = app['meetings'][meeting_name]
            host = meeting['host']

            return [{'username': participant, 'isHost': participant == host} for participant in meeting['participants']]

        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if data['type'] == 'create-meeting':
                        meeting_name = data['meetingName']
                        if meeting_name in app['meetings'].keys():
                            app['meetings'][meeting_name]['participants'].append(
                                data['username'])
                            app['meetings'][meeting_name]['host'] = data['username']
                        else:
                            app['meetings'][meeting_name] = {
                                'host': data['username'],
                                'participants': [data['username']],
                            }
                        msg = json.dumps(
                            {'type': 'participants-list', 'participants': participant_list(meeting_name)})
                        await ws.send_str(msg)
                    elif data['type'] == 'join-meeting':
                        meeting_name = data['meetingName']

                        if meeting_name in app['meetings'].keys():
                            app['meetings'][meeting_name]['participants'].append(
                                data['username'])
                        else:
                            app['meetings'][meeting_name] = {
                                'host': [data['username']],
                                'participants': [data['username']],
                            }
                        msg = json.dumps(
                            {'type': 'participants-list', 'participants': participant_list(meeting_name)})
                        for _ws in self.request.app['websockets']:
                            await _ws.send_str(msg)
                    elif data['type'] == 'send-message':
                        # Broadcast to everyone
                        data['type'] = "add-message"
                        msg = json.dumps(data)

                        for _ws in self.request.app['websockets']:
                            await _ws.send_str(msg)

                elif msg.type == aiohttp.WSMsgType.ERROR:
                    pass
        finally:
            self.request.app['websockets'].discard(ws)

        return ws


def add_cors_routes(routes, cors):
    for route in routes:
        cors.add(route, {
            "*":
            aiohttp_cors.ResourceOptions(
                expose_headers="*",
                allow_headers="*")
        })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="WebRTC audio / video"
    )
    # parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    # parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host for HTTP server (default: 0.0.0.0)"
    )
    # parser.add_argument(
    #     "--port", type=int, default=8080, help="Port for HTTP server (default: 8080)"
    # )
    parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()

    log_format =  "%(asctime)s %(levelname)s %(message)s"
    if args.verbose:
        logging.basicConfig(format=log_format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=log_format, level=logging.INFO)

    app = web.Application()
    app['websockets'] = weakref.WeakSet()
    app['meetings'] = dict()

    cors = aiohttp_cors.setup(app)

    app.on_shutdown.append(on_shutdown)

    static_route = app.router.add_static(
        '/static/', path=STATIC_PATH, name='static')
    app.router.add_get("/", index)

    post_route = app.router.add_post("/offer", offer)
    app.router.add_route('GET', '/ws', WebSocket)
    listener_route = app.router.add_post("/listen", listener)
    add_cors_routes([static_route, post_route, listener_route], cors)

    web.run_app(
        app, access_log=None, host=args.host, port=port
    )
