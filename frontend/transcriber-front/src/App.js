import React from 'react';
import logo from './logo.svg';
import './App.css';
import './components/audio/AudioComponent'
import {AudioComponent} from "./components/audio/AudioComponent";

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Hello!
        </p>
        <AudioComponent />
      </header>
    </div>
  );
}

export default App;
