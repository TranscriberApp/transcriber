import React from "react";
import { Button, Form, Input, Typography } from "antd";
import { UserOutlined } from "@ant-design/icons";
import { connect } from "react-redux";
import { rtcConnectionService } from "../../services/RTCConnectionService";
import Particler from "../../Particler";
const { Text } = Typography;

function EnterMeetingComponent(props) {
  return (
    <>
      <Text>Join a meeting</Text>

      <Form
        style={{ marginTop: 20 }}
        layout="vertical"
        size="large"
        onFinish={(s) => props.handleJoin(s.meeting, props.username)}
      >
        <Form.Item
          name="meeting"
          rules={[{ required: true, message: "Please input meeting id" }]}
        >
          <Input
            prefix={<UserOutlined className="site-form-item-icon" />}
            placeholder="Meeting ID"
          />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit">
            Join a meeting
          </Button>
        </Form.Item>
      </Form>
      <Text>or create your own one</Text>
      <Form
        style={{ marginTop: 20 }}
        layout="vertical"
        size="large"
        onFinish={(s) => props.handleCreate(s.meeting, props.username)}
      >
        <Form.Item
          name="meeting"
          rules={[{ required: true, message: "Please input meeting id" }]}
        >
          <Input
            prefix={<UserOutlined className="site-form-item-icon" />}
            placeholder="Meeting ID"
          />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit">
            Create a meeting
          </Button>
        </Form.Item>
      </Form>
    </>
  );
}

const mapStateToProps = state => {
  return {
    username: state.username
  };
};
const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    handleJoin: (meeting, username) => {
      dispatch({ type: "JOIN", meeting: meeting });
      ownProps.socket.send(
        JSON.stringify({ type: "join-meeting", username: username, meetingName: meeting })
      );
      rtcConnectionService.initConnectionListener();
    },
    handleCreate: (meeting, username) => {
      dispatch({ type: "CREATE", meeting: meeting });
      ownProps.socket.send(
        JSON.stringify({ type: "create-meeting", username: username, meetingName: meeting })
      );
      rtcConnectionService.initConnection();
    },
  };
};

export const EnterMeetingContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(EnterMeetingComponent);
