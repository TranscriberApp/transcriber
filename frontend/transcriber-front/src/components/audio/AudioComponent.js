import React from "react";

export class AudioComponent extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            audio: null,
            recorder: null,
            recordedData: null,
            recordingSrc: null,
        };

        this.websocket = new WebSocket("ws://192.168.0.1");
        this.toggleMicrophone = this.toggleMicrophone.bind(this);
        this.handleBlob = this.handleBlob.bind(this);
        this.getMicrophone = this.getMicrophone.bind(this);
        this.stopMicrophone = this.stopMicrophone.bind(this);
        this.toggleMicrophone = this.toggleMicrophone.bind(this);
        this.intervalCall = this.intervalCall.bind(this);
        setInterval(this.intervalCall, 1000)
    }

    handleBlob = (data) => {
        this.setState({recordedData: data});
        this.websocket.send(data);
    };

    intervalCall = () => {
        if(this.state.audio) {
            this.state.recorder.stop();
            this.state.recorder.start()
        }
    };

    async getMicrophone() {
        const audio = await navigator.mediaDevices.getUserMedia({
            audio: true,
            video: false
        });

        let mediaRecorder = new MediaRecorder(audio, {mimeType: 'audio/ogg'});
        mediaRecorder.ondataavailable = (e) => this.handleBlob(e.data);
        mediaRecorder.start();
        this.setState({audio, recorder: mediaRecorder});
    }

    stopMicrophone() {
        this.state.audio.getTracks().forEach(track => track.stop());
        this.state.recorder.stop();
        this.setState({audio: null, recorder: null, recordedData: null});
    }

    toggleMicrophone() {
        if (this.state.audio) {
            this.stopMicrophone();
        } else {
            this.getMicrophone();
        }
    }

    render() {
        return (
            <div className="controls">
                <button onClick={this.toggleMicrophone}>
                    {this.state.audio ? 'Stop microphone' : 'Turn on microphone'}
                </button>

                {this.state.recordedData && <audio id={"replay"} controls>
                    <source src={URL.createObjectURL(this.state.recordedData)} type={"audio/ogg"} />
                    Your browser does not support the audio element.
                </audio>}
            </div>
        );
    }
}