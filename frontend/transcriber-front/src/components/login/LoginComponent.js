import React from "react";
import {Button, Form, Input} from 'antd';
import {UserOutlined} from '@ant-design/icons';

export function LoginComponent(props) {
    return (
        <Form name="login" layout="vertical" size="large" onFinish={props.onFinish}>
            <Form.Item
                name="username"
                rules={[{required: true, message: 'Please input your username',},]}
            >
                <Input prefix={<UserOutlined className="site-form-item-icon"/>} placeholder="Username"/>
            </Form.Item>
            <Form.Item>
                <Button type="primary" htmlType="submit">
                    Start your journey
                </Button>
            </Form.Item>
        </Form>
    )
}

