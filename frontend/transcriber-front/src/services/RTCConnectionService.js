import socketIOClient from "socket.io-client";


class RTCConnectionService {
  constructor() {
    this.rtcConnection = new RTCPeerConnection({
      sdpSemantics: "unified-plan",
    });
    this.initConnection = this.initConnection.bind(this);

    // connect audio / video
    this.rtcConnection.addEventListener("track", function (evt) {
      console.log("incomming track");
      console.log(evt);
      if (evt.track.kind == "video") {
        document.getElementById("video").srcObject = evt.streams[0];
        console.log("video elem added");
      } else {
        const audioObj = document.getElementById("audio"); 
        console.log(audioObj);
        audioObj.srcObject = evt.streams[0];
        console.log(audioObj.srcObject);
        console.log(evt.streams[0])
      }
    });
  }

  async initConnection() {
    // const ws = new WebSocket("localhost:8080/test");

    const offerInit = await this.rtcConnection.createOffer({
      offerToReceiveVideo: false,
      offerToReceiveAudio: true,
    });
    await this.rtcConnection.setLocalDescription(
      new RTCSessionDescription(offerInit)
    );

    const offer = this.rtcConnection.localDescription;

    //   .then(() => {});``
    const resp = await fetch("http://localhost:8080/offer", {
      body: JSON.stringify({
        sdp: offer.sdp,
        type: offer.type,
        // video_transform: document.getElementById('video-transform').value
      }),
      headers: {
        "Content-Type": "application/json",
      },
      method: "POST",
    });
    const jsonResp = await resp.json();
    console.log("got response: ", jsonResp);
    console.log("answer sdp: ", jsonResp.sdp);
    await this.rtcConnection.setRemoteDescription(jsonResp);
  }
}

export let rtcConnectionService = new RTCConnectionService();
