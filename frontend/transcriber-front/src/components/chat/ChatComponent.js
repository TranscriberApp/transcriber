import React from "react";
import {Button, Form, Input, List, Typography} from "antd";
import {connect} from "react-redux";
import './ChatComponent.css'
import {UserOutlined} from "@ant-design/icons";
const {Text} = Typography;

class ChatComponent extends React.Component {
    constructor(props) {
        super(props);
        this.formRef = React.createRef();
    }
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
                <Form name="message" layout="horizontal" size="large" className={"send-msg-form"}
                      ref={this.formRef}
                      onFinish={s => {
                    this.props.sendMessage(s.msg, this.props.username)
                    console.log(this.formRef)
                    this.formRef.current.setFieldsValue({
                        msg: "",
                    })

                }}>
                    <Form.Item
                        name="msg"
                        rules={[{required: true, message: 'Please input your message',},]}
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