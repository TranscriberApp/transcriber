import React from "react";
import { List, Typography, Avatar } from "antd";
import { UserOutlined } from "@ant-design/icons";
import "./ParticipantsComponent.css";

const { Text } = Typography;

function renderParticipant(participant, currentUser) {
  return (
    <div className={["participant-container"]}>
      <Avatar
        shape="round"
        icon={<UserOutlined />}
        style={{ verticalAlign: "middle", color: "#1890ff"}}

      />
      <Text style={{ paddingLeft: 10 }}>{(participant.username !== currentUser && participant.username) || "You" }</Text>
        {participant.isHost && <Text>(host)</Text>}

    </div>
  );
}

export class ParticipantsComponent extends React.Component {
  constructor(props) {
    super(props);
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
            <List.Item>{renderParticipant(item, this.props.currentUser)}</List.Item>
          )}
        />
      </div>
    );
  }
}
