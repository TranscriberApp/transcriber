import argparse
import asyncio
import json
import logging
import os
import ssl
import uuid
import weakref

import aiohttp
import aiohttp_cors
from aiohttp import web
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

ROOT = os.path.dirname(__file__)

logger = logging.getLogger("pc")
speakers = set()
speakers_video = set()
listeners = set()
alltracks = set()
pcs = set()
meetings = dict()


class AudioTransformTrack(MediaStreamTrack):

    kind = "audio"

    def __init__(self, track):
        super().__init__()
        logger.info(f"added {track}")
        self.track = track

    async def recv(self):
        frame = await self.track.recv()
        return frame


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
    pcs.add(pc)

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
            print("added", local_audio)
        elif track.kind == "video":
            speakers.add(track)
            pc.addTrack(track)

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
                            app['meetings'][meeting_name]['participants'].append(data['username'])
                            app['meetings'][meeting_name]['host'] = data['username']
                        else:
                            app['meetings'][meeting_name] = {
                                'host': data['username'],
                                'participants': [data['username']],
                            }
                        msg = json.dumps({'type': 'participants-list', 'participants': participant_list(meeting_name)})
                        await ws.send_str(msg)
                    elif data['type'] == 'join-meeting':
                        meeting_name = data['meetingName']

                        if meeting_name in app['meetings'].keys():
                            app['meetings'][meeting_name]['participants'].append(data['username'])
                        else:
                            app['meetings'][meeting_name] = {
                                'host': [data['username']],
                                'participants': [data['username']],
                            }
                        msg = json.dumps({'type': 'participants-list', 'participants': participant_list(meeting_name)})
                        await ws.send_str(msg)
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="WebRTC audio / video"
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
    app['websockets'] = weakref.WeakSet()
    app['meetings'] = dict()

    cors = aiohttp_cors.setup(app)

    app.on_shutdown.append(on_shutdown)

    post_route = app.router.add_post("/offer", offer)
    app.router.add_route('GET', '/ws', WebSocket)
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
