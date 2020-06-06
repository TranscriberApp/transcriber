import socketIOClient from "socket.io-client";
import { start, startListener } from "../components/AudioTest";

class RTCConnectionService {
    constructor() {
        this.rtcConnection = new RTCPeerConnection({
            sdpSemantics: "unified-plan",
        });
        this.initConnection = this.initConnection.bind(this);


        // connect audio / video
        this.rtcConnection.addEventListener("track", function (evt) {

            if (evt.track.kind == "video") {

            } else {
                const audioObj = document.getElementById("audio");
                console.log(audioObj);
                audioObj.srcObject = evt.streams[0];
                console.log(audioObj.srcObject);
                console.log(evt.streams[0])
            }
        });
    }

    mute() {
        this.audio.getAudioTracks()[0].enabled = false
    }

    unmute() {
        this.audio.getAudioTracks()[0].enabled = true
    }

    async initConnection() {
        // navigator.mediaDevices.getUserMedia({
        //     audio: true,
        //     video: false,
        // }).then(audio => {
        //     this.audio = audio;
        //     audio.getTracks()
        //         .forEach((track) =>
        //             rtcConnectionService.rtcConnection.addTrack(track, audio)
        //         );
        //     return this.rtcConnection.createOffer({
        //         offerToReceiveVideo: false,
        //         offerToReceiveAudio: true,
        //     })
        // }).then(offer => this.rtcConnection.setLocalDescription(offer))
        //     .then(() => {
        //         const connection = this.rtcConnection;
        //         console.log(connection)
        //         return new Promise(function (resolve) {
        //             if (connection.iceGatheringState === 'complete') {
        //                 resolve();
        //             } else {
        //                 function checkState() {
        //                     if (connection.iceGatheringState === 'complete') {
        //                         connection.removeEventListener('icegatheringstatechange', checkState);
        //                         resolve();
        //                     }
        //                 }

        //                 connection.addEventListener('icegatheringstatechange', checkState);
        //             }
        //         })
        //     }).then(() => {
        //     const offer = this.rtcConnection.localDescription
        //     return fetch("http://localhost:8080/offer", {
        //         body: JSON.stringify({
        //             sdp: offer.sdp,
        //             type: offer.type,
        //             // video_transform: document.getElementById('video-transform').value
        //         }),
        //         headers: {
        //             "Content-Type": "application/json",
        //         },
        //         method: "POST",
        //     });
        // }).then(response => response.json())
        //     .then(answer => this.rtcConnection.setRemoteDescription(answer))
        start();
    }

    async stopConnection() {
      if (this.rtcConnection.getTransceivers) {
        this.rtcConnection.getTransceivers().forEach(function(transceiver) {
          if (transceiver.stop) {
            transceiver.stop();
          }
        });
      }

      // close local audio / video
      this.rtcConnection.getSenders().forEach(function(sender) {
        sender.track.stop();
      });

      // close peer connection
      const connection = this.rtcConnection;
      setTimeout(function() {
        connection.close();
      }, 500);
    }

    async initConnectionListener() {
      startListener();
    }
}

export let rtcConnectionService = new RTCConnectionService();
