import React from "react";
import { List, Typography, Avatar } from "antd";
import { UserOutlined } from "@ant-design/icons";
import "./ParticipantsComponent.css";

const { Text } = Typography;

function renderParticipant(participant) {
  return (
    <div className={"participant-container"}>
      <Avatar
        shape="round"
        icon={<UserOutlined />}
        style={{ verticalAlign: "middle" }}
      />
      <Text style={{ paddingLeft: 10 }}>{participant.username}</Text>
    </div>
  );
}

export class ParticipantsComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      participants: [
        { username: "myrmarachne" },
        { username: "Itachi" },
        { username: "Kira" },
      ],
    };
  }

  render() {
    return (
      <div className={"participants-list-container"}>
        <List
          header={
            <Text strong className={"header-text"}>
              Participants
            </Text>
          }
          className={"participants-list"}
          bordered
          dataSource={this.props.participants}
          renderItem={(item) => (
            <List.Item>{renderParticipant(item)}</List.Item>
          )}
        />
      </div>
    );
  }
}
