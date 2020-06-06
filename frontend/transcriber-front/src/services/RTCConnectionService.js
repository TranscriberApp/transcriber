import socketIOClient from "socket.io-client";

class RTCConnectionService {
    constructor() {
        this.rtcConnection = new RTCPeerConnection();
        this.initConnection = this.initConnection.bind(this);
    }

    async initConnection() {
        const socket = socketIOClient("localhost:1234");

        const offer = await this.rtcConnection.createOffer();
        this.rtcConnection.setLocalDescription(new RTCSessionDescription(offer)).then(() => {
            socket.on('answer', data => {
                console.log('received answer ' + data.toString());
                this.rtcConnection.setRemoteDescription(data.data)
            });
            socket.emit('offer', offer);
        });
    }
}

export let rtcConnectionService = new RTCConnectionService();
