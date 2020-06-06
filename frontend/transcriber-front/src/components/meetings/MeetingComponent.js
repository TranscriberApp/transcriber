import React from "react";
import { TranscriptComponent } from "../transcript/TranscriptComponent";
import { ParticipantsComponent } from "../participants/ParticipantsComponent";
import { Col, Row } from "antd";
import { AudioComponent } from "../audio/AudioComponent";
import { connect } from "react-redux";
import { ChatContainer } from "../chat/ChatComponent";
import './MeetingComponent.css';

class MeetingComponent extends React.Component {
  constructor(props) {
    super(props);
    this.socket = new WebSocket("ws://192.168.0.1");
    this.socket.onmessage = (ev) => {
      switch (ev.data.type) {
        case "participants-list":
          props.updateParticipantsList(ev.data.participants);
          break;
        case "add-message":
          props.receivedMessage(ev.data.msg);
          break;
        default:
          console.log("Can't understand that message" + ev.data);
          break;
      }
    };
  }
  render() {
    return (
      <div className={"meeting-container"}>
        <Row>
          <Col span={24}>
            <h2>Meeting name: {this.props.meeting}</h2>
          </Col>
        </Row>
        <div style={{ display: "none" }}>
          <Row>
            <div id="media" style={{ display: "none" }}>
              <audio id="audio" autoPlay={true}></audio>
              <video id="video" autoPlay={true} playsInline={true}></video>
            </div>
          </Row>
        </div>
        <Row>
          <Col span={16}>
            <TranscriptComponent />
          </Col>
          <Col span={8}>
            <ParticipantsComponent participants={this.props.participants} />
          </Col>
          <Col span={24}>
            <ChatContainer
              messages={this.props.messages}
              sendMessage={this.props.sendMessage}
            />
          </Col>
          <Col span={24}>
            <AudioComponent isHost={this.props.isHost} />
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
const mapDispatchToProps = (dispatch) => {
  return {
    updateParticipantsList: (participants) =>
      dispatch({ type: "SET_PARTICIPANTS_LIST", participants: participants }),
    receivedMessage: (msg) => dispatch({ type: "RECEIVED_MESSAGE", msg: msg }),
    sendMessage: (msg, author) => {
      console.log("Send " + msg.toString())
      this.socket.send(JSON.stringify({type: 'add-message', msg: msg, author: author}))
    }
  };
};

export const MeetingContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(MeetingComponent);
