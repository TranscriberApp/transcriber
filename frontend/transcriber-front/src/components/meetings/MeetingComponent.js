import React from "react";
import {TranscriptComponent} from "../transcript/TranscriptComponent";
import {ParticipantsComponent} from "../participants/ParticipantsComponent";
import { Row, Col } from 'antd';
import {AudioComponent} from "../audio/AudioComponent";

export class MeetingComponent extends React.Component {

    render() {
        return (
            <>
                <Row>
                    <Col span={24}><h2>Meeting name</h2></Col>
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
        )
    }
}