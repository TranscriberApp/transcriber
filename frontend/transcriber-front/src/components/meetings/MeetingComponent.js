import React from "react";
import { TranscriptComponent } from "../transcript/TranscriptComponent";
import { ParticipantsComponent } from "../participants/ParticipantsComponent";
import { Col, Row } from "antd";
import { AudioComponent } from "../audio/AudioComponent";
import { connect } from "react-redux";
import { ChatContainer } from "../chat/ChatComponent";
import "./MeetingComponent.css";

class MeetingComponent extends React.Component {
  constructor(props) {
    super(props);
  }
  render() {
    return (
      <div className={"meeting-container"}>
        <Row>
          <Col span={24}>
            <h2>Meeting name: {this.props.meeting}</h2>
          </Col>
        </Row>
        <Row>
          <div id="media" style={{ display: "none" }}>
            <audio id="audio" autoPlay={true}></audio>
            <video id="video" autoPlay={true} playsInline={true}></video>
          </div>
        </Row>
        <Row>
          <Col span={16}>
            <TranscriptComponent />
          </Col>
          <Col span={8}>
            <AudioComponent isHost={this.props.isHost} />
            <ParticipantsComponent
              participants={this.props.participants}
              currentUser={this.props.username}
            />
          </Col>
          <Col span={24}>
            <ChatContainer
              messages={this.props.messages}
              sendMessage={this.props.sendMessage}
            />
          </Col>
        </Row>
      </div>
    );
  }
}

const mapStateToProps = (state) => {
  return {
    username: state.username,
    meeting: state.meeting,
    participants: state.participants,
    isHost: state.isHost,
    messages: state.messages,
  };
};

export const MeetingContainer = connect(mapStateToProps)(MeetingComponent);
