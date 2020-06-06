import React from "react";
import {Button, Form, Input} from "antd";
import {UserOutlined} from "@ant-design/icons";
import {connect} from "react-redux";

function EnterMeetingComponent(props) {
    return (
        <Form layout="vertical" size="large" onFinish={s => props.handleJoin(s.meeting)}>
            <Form.Item
                name="meeting"
                rules={[{required: true, message: 'Please input meeting id',},]}
            >
                <Input prefix={<UserOutlined className="site-form-item-icon"/>} placeholder="Meeting ID"/>
            </Form.Item>
            <Form.Item>
                <Button type="primary" htmlType="submit">
                    Join a meeting
                </Button>
            </Form.Item>
        </Form>
    )
}

const mapStateToProps = () => {
    return {}
};
const mapDispatchToProps = dispatch => {
    return {
        handleJoin: meeting => dispatch({type: 'JOIN', meeting: meeting})
    }
};

export const EnterMeetingContainer = connect(mapStateToProps, mapDispatchToProps)(EnterMeetingComponent);
