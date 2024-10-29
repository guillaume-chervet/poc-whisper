import './App.css'
import AudioRecorderComponent from "./AudioRecorderComponent.jsx";

function App() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
       return (
        <div className="App">
          <AudioRecorderComponent />
        </div>
      );
    } else {
        console.error("L'API mediaDevices n'est pas supportée par ce navigateur.");
        return (
            <div className="App">
              <p>L'API mediaDevices n'est pas supportée par ce navigateur.</p>
            </div>
          );
    }

}

export default App
