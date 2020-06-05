import React from "react";

export class AudioComponent extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            audio: null,
        };

        this.rtcConnection = new RTCPeerConnection();
        this.toggleMicrophone = this.toggleMicrophone.bind(this);
        this.turnOnMicrophone = this.turnOnMicrophone.bind(this);
        this.turnOffMicrophone = this.turnOffMicrophone.bind(this);
    }

    async turnOnMicrophone() {
        const audio = await navigator.mediaDevices.getUserMedia({
            audio: true,
            video: false
        });
        this.rtcConnection.addStream(audio)
        audio.getTracks().forEach(track => this.rtcConnection.addTrack(track, audio));

        this.setState({audio});
    }

    turnOffMicrophone() {
        this.state.audio.getTracks().forEach(track => track.stop());
        this.state.recorder.stop();
        this.setState({audio: null, recorder: null, recordedData: null});
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
                <button onClick={this.toggleMicrophone}>
                    {this.state.audio ? 'Turn off microphone' : 'Turn on microphone'}
                </button>
            </div>
        );
    }
}