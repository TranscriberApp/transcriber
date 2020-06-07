const webRtcServiceUrl = process.env.REACT_APP_WEBRTC_SERVICE;
const websocketServiceUrl = process.env.REACT_APP_WEBSOCKET_SERVICE;

console.log("webrtc url: ", webRtcServiceUrl);
console.log("websocket url: ", websocketServiceUrl);
export { webRtcServiceUrl, websocketServiceUrl };
