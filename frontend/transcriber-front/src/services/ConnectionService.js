
class ConnectionService {
    constructor(wsAddress) {
        this.rtcConnection = new RTCPeerConnection();
        this.webSocket = new WebSocket(wsAddress);
        this.initConnection = this.initConnection.bind(this);
    }

    async initConnection() {
        const offer = await this.rtcConnection.createOffer();
        let webSocket = this.webSocket
        this.rtcConnection.setLocalDescription(new RTCSessionDescription(offer)).then(() => {
            webSocket.onmessage = async event => {
                const msg = JSON.parse(event.data);
                switch(msg.type) {
                    case "server-answer":
                        await this.rtcConnection.setRemoteDescription(msg.answer);
                        break;
                    default:
                        console.log("Can't understand message");
                        break;
                }
            };
            webSocket.send(JSON.stringify({
                type: "connect-to-server",
                offer
            }));
        });
    }
}


export let connectionService = new ConnectionService("ws://192.168.0.1");
