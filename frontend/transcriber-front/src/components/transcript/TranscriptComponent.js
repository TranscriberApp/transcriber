import React from "react";
import {Typography, Space, List} from "antd";
import './TranscriptComponent.css';
const {Text} = Typography;

export class TranscriptComponent extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            transcriptParts: [{speaker: "Hamilton", text: "The first words"}, {speaker: "Bell", text: "and the answer"},
                {speaker: "Machine", text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor " +
                        "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco " +
                        "laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit " +
                        "esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui" +
                        " officia deserunt mollit anim id est laborum"},
                {speaker: "Sokrates", text: "I do nothing but go about persuading you all, old and young alike, not to take thought for your" +
                        " persons or your properties, but and chiefly to care about the greatest improvement of the soul. I tell you that virtue " +
                        "is not given by money, but that from virtue comes money and every other good of man, public as well as private. This is my" +
                        " teaching, and if this is the doctrine which corrupts the youth, I am a mischievous person. "},
                {speaker: "Hamilton", text: "The first words"}, {speaker: "Bell", text: "and the answer"}]
        };
        this.addTranscript = this.addTranscript.bind(this);
        this.socket = new WebSocket("ws://192.168.0.1");
        this.socket.onmessage = event => this.addTranscript(JSON.parse(event.data));
    }


    addTranscript(transcriptPart) {
        this.setState({
            transcriptParts: this.state.transcriptParts.concat(transcriptPart)
        });
    }

    render() {
        return (
            <div className="transcript-container">
                <List
                    className={"transcript-list"}
                    header={<Text className={"transcript-header"} strong>Transcript</Text>}
                    bordered
                    dataSource={this.state.transcriptParts}
                    renderItem={item => <List.Item className={"transcript-item"}><Text>{item.text}</Text></List.Item>}
                />
            </div>
        )
    }
}
