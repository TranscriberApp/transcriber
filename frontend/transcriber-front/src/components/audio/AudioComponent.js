import React from "react";
import {rtcConnectionService} from '../../services/RTCConnectionService'
import {Button} from "antd";

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
        rtcConnectionService.rtcConnection.ontrack = event => {
            this.setState({audioSource: event.source});
        };
    }

    async turnOnMicrophone() {
        const audio = await navigator.mediaDevices.getUserMedia({
            audio: true,
            video: false
        });
        audio.getTracks().forEach(track => rtcConnectionService.rtcConnection.addTrack(track, audio));
        this.setState({audio});
    }

    turnOffMicrophone() {
        this.state.audio.getTracks().forEach(track => track.stop());
        this.setState({audio: null});
    }

    toggleMicrophone() {
        if (this.state.audio) {
            this.turnOffMicrophone();
        } else {
            this.turnOnMicrophone();
        }
    }

    render() {
        return (
            <div className="controls">
                <Button type="primary" onClick={this.toggleMicrophone}>
                    {this.state.audio ? 'Turn off microphone' : 'Turn on microphone'}
                </Button>
                {this.state.audioSource && <audio controls src={this.state.audioSource}/>}
            </div>
        );
    }
}