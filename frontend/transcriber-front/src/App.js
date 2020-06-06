import React from "react";
import "./App.css";
import "./components/audio/AudioComponent";
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
