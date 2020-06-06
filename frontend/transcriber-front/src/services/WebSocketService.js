class WebSocketService {
  constructor(wsAddress) {
    this.webSocket = new WebSocket(wsAddress);
    this.listeners = {};
    this.addListener = this.addListener.bind(this);
    this.removeListener = this.removeListener.bind(this);
    this.handleMessage = this.handleMessage.bind(this);

    this.webSocket.onmessage = async (event) => this.handleMessage(event);
  }

  addListener(msgType, listener) {
    this.listeners[msgType] = (this.listeners[msgType] || []).concat(listener);
  }

  removeListener(msgType, listener) {
    this.listeners[msgType] = (this.listeners[msgType] || []).filter(
      (l) => l !== listener
    );
  }

  handleMessage(event) {
    let msg = JSON.parse(event.data);
    (this.listeners[msg.type] || []).forEach((listener) => listener(msg));
  }
}

export const webSocketService = new WebSocketService(
  "ws://192.168.1.14:8080/ws"
);
