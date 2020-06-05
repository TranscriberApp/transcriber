import React from 'react';
import logo from './logo.svg';
import './App.css';
import './components/audio/AudioComponent'
import {AudioComponent} from "./components/audio/AudioComponent";
import {rtcConnectionService} from "./services/RTCConnectionService";
import {LoginComponent} from "./components/login/LoginComponent";
import 'antd/dist/antd.css';

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            username: undefined
        }
    }
    render() {
        return (
            <div className="App">
                <header className="App-header">
                    <img src={logo} className="App-logo" alt="logo"/>
                    <p>
                        Hello {this.state.username}!
                    </p>
                    {!this.state.username && <LoginComponent onFinish={value => this.setState({username: value.username})}/>}
                    <button onClick={rtcConnectionService.initConnection}>
                        Init connection
                    </button>
                    <AudioComponent/>
                </header>
            </div>
        );
    }
}

export default App;
