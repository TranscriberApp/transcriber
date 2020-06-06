import React from "react";
import { rtcConnectionService } from "../../services/RTCConnectionService";
import { Button } from "antd";

export class AudioComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      microphoneOn: true
    };

    this.toggleMicrophone = this.toggleMicrophone.bind(this);
    this.turnOnMicrophone = this.turnOnMicrophone.bind(this);
    this.turnOffMicrophone = this.turnOffMicrophone.bind(this);
  }

  toggleMicrophone() {
    if (this.state.microphoneOn) {
      this.turnOffMicrophone();
    } else {
      this.turnOnMicrophone();
    }
  }

  async turnOnMicrophone() {
    rtcConnectionService.unmute()
    this.setState({ microphoneOn: true});
  }

  turnOffMicrophone() {
    rtcConnectionService.mute()
    this.setState({ microphoneOn: false });
  }

  render() {
    return (
      <div className="controls">
        <Button type="primary" onClick={this.toggleMicrophone}>
          {this.state.microphoneOn ? "Turn off microphone" : "Turn on microphone"}
        </Button>
        {this.state.microphoneOn && (
          <Button onClick={() => rtcConnectionService.stopConnection()}>Stop session</Button>
        )}
      </div>
    );
  }
}
