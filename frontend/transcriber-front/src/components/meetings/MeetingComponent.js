import React from "react";
import { TranscriptComponent } from "../transcript/TranscriptComponent";
import { ParticipantsComponent } from "../participants/ParticipantsComponent";
import { Col, Row } from "antd";
import { AudioComponent } from "../audio/AudioComponent";

export function MeetingComponent(props) {
  return (
    <>
      <Row>
        <Col span={24}>
          <h2>Meeting name: {props.name}</h2>
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
          <ParticipantsComponent />
        </Col>
        <Col span={24}>
          <AudioComponent />
        </Col>
      </Row>
    </>
  );
}
