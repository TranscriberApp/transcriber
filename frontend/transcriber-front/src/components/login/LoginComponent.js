import React from "react";
import { Button, Form, Input } from "antd";
import { UserOutlined } from "@ant-design/icons";
import { connect } from "react-redux";
import { Container } from "semantic-ui-react";
import Particler from "../../Particler";

function LoginComponent(props) {
  return (
    <>
      <Container>
        <Form
          name="login"
          layout="vertical"
          size="large"
          onFinish={(s) => props.handleLogin(s.username)}
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: "Please input your username" }]}
          >
            <Input
              prefix={<UserOutlined className="site-form-item-icon" />}
              placeholder="Username"
            />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              Start your journey
            </Button>
          </Form.Item>
        </Form>
      </Container>
    </>
  );
}

const mapStateToProps = () => {
  return {};
};
const mapDispatchToProps = (dispatch) => {
  return {
    handleLogin: (username) => dispatch({ type: "LOGIN", username: username }),
  };
};

export const LoginContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(LoginComponent);
