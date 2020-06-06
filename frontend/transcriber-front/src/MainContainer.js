import React from "react";
import logo from "./logo.svg";
import "./App.css";
import "./components/audio/AudioComponent";
import { rtcConnectionService } from "./services/RTCConnectionService";
import { LoginContainer } from "./components/login/LoginComponent";
import "antd/dist/antd.css";

import { MeetingContainer } from "./components/meetings/MeetingComponent";
import { Button } from "antd";
import { connect } from "react-redux";
import { EnterMeetingContainer } from "./components/meetings/EnterMeetingComponent";

class MainComponent extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div className="App">
        <div className="App-header">
          {this.props.username  &&!this.props.meeting  && <p>Hello {this.props.username}!</p>}
          {!this.props.username && (
            <>
              <p>Hello Stranger!</p>
              <p>What is your name?</p>
            </>
          )}
          {!this.props.username && <LoginContainer />}
          {this.props.username && !this.props.meeting && (
            <EnterMeetingContainer />
          )}
        </div>
        {this.props.username && this.props.meeting && (
          <div className="main-container">
            <MeetingContainer />
            <div>
              <div id="data-channel"></div>
              <div id="ice-connection-state"></div>
              <div id="ice-gathering-state"></div>
              <div id="signaling-state"></div>
            </div>
          </div>
        )}
      </div>
    );
  }
}

const mapStateToProps = (state) => {
  return {
    username: state.username,
    meeting: state.meeting,
  };
};

export const MainContainer = connect(mapStateToProps)(MainComponent);
