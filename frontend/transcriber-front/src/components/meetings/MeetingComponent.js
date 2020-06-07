import React from "react";
import { TranscriptComponent } from "../transcript/TranscriptComponent";
import { ParticipantsComponent } from "../participants/ParticipantsComponent";
import { Col, Row, Button } from "antd";
import { AudioComponent } from "../audio/AudioComponent";
import { connect } from "react-redux";
import { ChatContainer } from "../chat/ChatComponent";
import "./MeetingComponent.css";
import { rtcConnectionService } from "../../services/RTCConnectionService";
import { List } from "antd/lib/form/Form";
import Text from "antd/lib/typography/Text";
import { Segment } from "semantic-ui-react";

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
          <Col span={8}>
            <div id="media" style={{ display: "inline-block" }}>
              <audio id="audio" autoPlay={true}></audio>
              <Text strong className={"header-text"}>
                Presenter video
              </Text>
              <Segment basic>
                <video
                  style={{ borderRadius: "15px" }}
                  id="video"
                  autoPlay={true}
                  playsInline={true}
                ></video>
              </Segment>
            </div>
          </Col>
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
          <Col span={24}>
            <AudioComponent isHost={this.props.isHost} />
          </Col>
          <Col span={24}>
            <Button onClick={() => rtcConnectionService.initConnection()}>
              Retry connection
            </Button>
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
      console.log("Send " + msg.toString());
      this.socket.send(
        JSON.stringify({ type: "add-message", msg: msg, author: author })
      );
    },
  };
};

export const MeetingContainer = connect(mapStateToProps)(MeetingComponent);
