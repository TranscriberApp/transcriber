import React from "react";
import logo from "./logo.svg";
import "./App.css";
import "./components/audio/AudioComponent";
import { LoginComponent } from "./components/login/LoginComponent";
import "antd/dist/antd.css";

import {store} from "./redux/store";
import {Provider} from "react-redux";
import {MainContainer} from "./MainContainer";

class App extends React.Component {
  constructor(props) {
    super(props);
  }
  render() {
    return (
        <Provider store={store}>
          <MainContainer />
        </Provider>
    );
  }
}

export default App;
