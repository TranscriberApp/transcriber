import argparse
import asyncio
import json
import logging
import os
import ssl
import uuid

import aiohttp_cors
# import cv2
from aiohttp import web
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
from av import VideoFrame

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

        # logger.info(f"Got a new frame!!!! {frame}")

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

    # async def recv(self):
    #     frame = await self.track.recv()

    #     if self.transform == "cartoon":
    #         img = frame.to_ndarray(format="bgr24")

    #         # prepare color
    #         img_color = cv2.pyrDown(cv2.pyrDown(img))
    #         for _ in range(6):
    #             img_color = cv2.bilateralFilter(img_color, 9, 9, 7)
    #         img_color = cv2.pyrUp(cv2.pyrUp(img_color))

    #         # prepare edges
    #         img_edges = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    #         img_edges = cv2.adaptiveThreshold(
    #             cv2.medianBlur(img_edges, 7),
    #             255,
    #             cv2.ADAPTIVE_THRESH_MEAN_C,
    #             cv2.THRESH_BINARY,
    #             9,
    #             2,
    #         )
    #         img_edges = cv2.cvtColor(img_edges, cv2.COLOR_GRAY2RGB)

    #         # combine color and edges
    #         img = cv2.bitwise_and(img_color, img_edges)

    #         # rebuild a VideoFrame, preserving timing information
    #         new_frame = VideoFrame.from_ndarray(img, format="bgr24")
    #         new_frame.pts = frame.pts
    #         new_frame.time_base = frame.time_base
    #         return new_frame
    #     elif self.transform == "edges":
    #         # perform edge detection
    #         img = frame.to_ndarray(format="bgr24")
    #         img = cv2.cvtColor(cv2.Canny(img, 100, 200), cv2.COLOR_GRAY2BGR)

    #         # rebuild a VideoFrame, preserving timing information
    #         new_frame = VideoFrame.from_ndarray(img, format="bgr24")
    #         new_frame.pts = frame.pts
    #         new_frame.time_base = frame.time_base
    #         return new_frame
    #     elif self.transform == "rotate":
    #         # rotate image
    #         img = frame.to_ndarray(format="bgr24")
    #         rows, cols, _ = img.shape
    #         M = cv2.getRotationMatrix2D(
    #             (cols / 2, rows / 2), frame.time * 45, 1)
    #         img = cv2.warpAffine(img, M, (cols, rows))

    #         # rebuild a VideoFrame, preserving timing information
    #         new_frame = VideoFrame.from_ndarray(img, format="bgr24")
    #         new_frame.pts = frame.pts
    #         new_frame.time_base = frame.time_base
    #         return new_frame
    #     else:
    #         return frame


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
    
    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)
        if track.kind == "audio":
            for speaker in speakers:
                log_info("adding speakers")
                pc.addTrack(speaker)

        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)


    # handle offer
    await pc.setRemoteDescription(offer)
    # await recorder.start()

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
    # if args.write_audio:
    #     log_info(f"recording to {args.write_audio}")
    #     recorder = MediaRecorder(args.write_audio)
    # else:
    #     recorder = MediaBlackhole()

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
    # await recorder.start()

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
