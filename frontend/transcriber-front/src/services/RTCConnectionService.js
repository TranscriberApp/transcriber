import {webSocketService} from "./WebSocketService";

class RTCConnectionService {
    constructor() {
        this.rtcConnection = new RTCPeerConnection();
        this.initConnection = this.initConnection.bind(this);
    }

    async initConnection() {
        const offer = await this.rtcConnection.createOffer();
        this.rtcConnection.setLocalDescription(new RTCSessionDescription(offer)).then(() => {
            webSocketService.addListener("server-answer", msg => this.rtcConnection.setRemoteDescription(msg.answer));
            webSocketService.webSocket.send(JSON.stringify({
                type: "connect-to-server",
                offer
            }));
        });
    }
}


export let rtcConnectionService = new RTCConnectionService("ws://192.168.0.1");
