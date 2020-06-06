import React from "react";
import logo from "./logo.svg";
import "./App.css";
import "./components/audio/AudioComponent";
import { rtcConnectionService } from "./services/RTCConnectionService";
import { LoginContainer } from "./components/login/LoginComponent";
import "antd/dist/antd.css";

import { MeetingComponent } from "./components/meetings/MeetingComponent";
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
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <p>Hello {this.props.username}!</p>
          {!this.props.username && <LoginContainer />}
          {this.props.username && !this.props.meeting && (
            <EnterMeetingContainer />
          )}
        </header>
        {this.props.username && this.props.meeting && (
          <div className="main-container">
            <MeetingComponent name={this.props.meeting} />
            <div>
              <div id="data-channel"></div>
              <div id="ice-connection-state"></div>
              <div id="ice-gathering-state"></div>
              <div id="signaling-state"></div>
              <Button
                type="primary"
                onClick={rtcConnectionService.initConnection}
              >
                Init connection
              </Button>

              <Button
                type="primary"
                onClick={rtcConnectionService.initConnectionListener}
              >
                Init connection as listener
              </Button>
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
