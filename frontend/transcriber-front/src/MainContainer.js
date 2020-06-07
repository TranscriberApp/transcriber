import React from "react";
import logo from "./logo.svg";
import "./App.css";
import "./components/audio/AudioComponent";
import { rtcConnectionService } from "./services/RTCConnectionService";
import { LoginContainer } from "./components/login/LoginComponent";
import "antd/dist/antd.css";

import { MeetingContainer } from "./components/meetings/MeetingComponent";
import { Segment, Container, Header, Icon } from "semantic-ui-react";
import { Button, Divider } from "antd";
import { connect } from "react-redux";
import { EnterMeetingContainer } from "./components/meetings/EnterMeetingComponent";
import Particles from "react-particles-js";
import Particler from "./Particler";

class MainComponent extends React.Component {
  socket = new WebSocket("ws://192.168.1.14:8080/ws");
  constructor(props) {
    super(props);
  }

  componentDidMount() {
    this.socket.onmessage = (ev) => {
      let data = JSON.parse(ev.data);
      console.log(data);
      switch (data.type) {
        case "participants-list":
          this.props.updateParticipantsList(data.participants);
          break;
        case "add-message":
          this.props.receivedMessage(data.msg, data.username);
          break;
        default:
          console.log("Can't understand that message" + ev.data);
          break;
      }
    };
  }

  render() {
    return (
      <>
        {!(this.props.meeting && this.props.username) && <Particler />}
        <div className="App">
          <div className="App-header">
            {!this.props.username && (
              <>
                <Header as="h1" icon>
                  <Icon name="tty" />
                  Transcriber
                  <Header.Subheader>
                    Connect your webinar-style meetings with our live
                    transcription service
                  </Header.Subheader>
                </Header>
                <Divider />
              </>
            )}
            {this.props.username && !this.props.meeting && (
              <>
                <Header as="h2">Hello {this.props.username}!</Header>
                <Divider />
              </>
            )}
            {!this.props.username && (
              <>
                <p>Please identify yourself below!</p>
              </>
            )}
            {!this.props.username && <LoginContainer />}
            {this.props.username && !this.props.meeting && (
              <EnterMeetingContainer socket={this.socket} />
            )}
          </div>
          {this.props.username && this.props.meeting && (
            <div className="main-container">
              <MeetingContainer
                sendMessage={(msg, username) => {
                  console.log("Send " + msg.toString());
                  this.socket.send(
                    JSON.stringify({
                      type: "send-message",
                      msg: msg,
                      username: username,
                    })
                  );
                }}
              />
              <div>
                <div id="data-channel"></div>
                <div id="ice-connection-state"></div>
                <div id="ice-gathering-state"></div>
                <div id="signaling-state"></div>
              </div>
            </div>
          )}
        </div>
      </>
    );
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    updateParticipantsList: (participants) =>
      dispatch({ type: "SET_PARTICIPANTS_LIST", participants: participants }),
    receivedMessage: (msg, username) => {
      console.log("RECEIVED MSG");
      dispatch({ type: "RECEIVED_MESSAGE", msg: msg, username: username });
    },
  };
};

const mapStateToProps = (state) => {
  return {
    username: state.username,
    meeting: state.meeting,
  };
};

export const MainContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(MainComponent);
