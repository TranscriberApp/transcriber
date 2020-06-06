import React from "react";
import {Button, Form, Input, List, Typography} from "antd";
import {connect} from "react-redux";
import './ChatComponent.css'
import {UserOutlined} from "@ant-design/icons";
const {Text} = Typography;

class ChatComponent extends React.Component {
    render() {
        return (
            <div className={"chat-container"}>
                <List
                    className={"chat-list"}
                    header={<Text className={"chat-header"} strong>Chat messages</Text>}
                    bordered
                    dataSource={this.props.messages}
                    renderItem={item => <List.Item className={"chat-item"}><Text type="secondary"><strong>{item.author}</strong>: {item.msg}</Text></List.Item>}
                />
                <Form name="message" layout="horizontal" size="large" className={"send-msg-form"} onFinish={s => {
                    this.props.sendMessage(s.msg, this.props.username)
                }}>
                    <Form.Item
                        name="msg"
                        rules={[{required: true, message: 'Please input your username',},]}
                    >
                        <Input prefix={<UserOutlined className="site-form-item-icon"/>} placeholder="Your message..."/>
                    </Form.Item>
                    <Form.Item>
                        <Button type="primary" htmlType="submit">
                            Send
                        </Button>
                    </Form.Item>
                </Form>
            </div>
        )
    }
}


const mapStateToProps = state => {
    return {
        username: state.username,
    };
};
const mapDispatchToProps = (dispatch) => {
    return {

    };
};

export const ChatContainer = connect(
    mapStateToProps,
    mapDispatchToProps
)(ChatComponent);