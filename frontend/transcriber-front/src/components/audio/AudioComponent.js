import React from "react";
import { rtcConnectionService } from "../../services/RTCConnectionService";
import { Button } from "antd";

export class AudioComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      audio: null,
      audioSource: null,
    };

    this.toggleMicrophone = this.toggleMicrophone.bind(this);
    this.turnOnMicrophone = this.turnOnMicrophone.bind(this);
    this.turnOffMicrophone = this.turnOffMicrophone.bind(this);
    rtcConnectionService.rtcConnection.ontrack = (event) => {
      console.log("got audio track");
      this.setState({ audioSource: event.source });
    };
  }

  toggleMicrophone() {
    if (this.state.audio) {
      this.turnOffMicrophone();
    } else {
      this.turnOnMicrophone();
    }
  }

  async turnOnMicrophone() {
    const audio = await navigator.mediaDevices.getUserMedia({
      audio: true,
      video: false,
    });
    audio
      .getTracks()
      .forEach((track) =>
        rtcConnectionService.rtcConnection.addTrack(track, audio)
      );
    this.setState({ audio });
  }

  turnOffMicrophone() {
    this.state.audio.getTracks().forEach((track) => {
      track.stop();
      track.dispatchEvent(new Event("ended"));
    });
    this.setState({ audio: null });
  }

  stopSession() {
    console.log("stopping");
    this.turnOffMicrophone();
    // close transceivers
    if (rtcConnectionService.rtcConnection.getTransceivers) {
      rtcConnectionService.rtcConnection
        .getTransceivers()
        .forEach(function (transceiver) {
          if (transceiver.stop) {
            transceiver.dispatchEvent(new Event("ended"));
            transceiver.stop();
          }
        });
    }

    // close local audio / video
    rtcConnectionService.rtcConnection.getSenders().forEach(function (sender) {
      sender.track.dispatchEvent(new Event("ended"));
      sender.track.stop();
      sender.track.dispatchEvent(new Event("ended"));
    });

    setTimeout(() => {
      rtcConnectionService.rtcConnection.close();
      console.log("closed!");
      rtcConnectionService.rtcConnection = new RTCPeerConnection({
        sdpSemantics: "unified-plan",
      });
    }, 500);
  }

  render() {
    return (
      <div className="controls">
        <Button type="primary" onClick={this.toggleMicrophone}>
          {this.state.audio ? "Turn off microphone" : "Turn on microphone"}
        </Button>
        {this.state.audio && (
          <Button onClick={() => this.stopSession()}>Stop session</Button>
        )}
        {this.state.audioSource && (
          <audio controls src={this.state.audioSource} />
        )}
      </div>
    );
  }
}
