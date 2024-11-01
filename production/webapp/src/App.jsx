import './App.css'
import AudioRecorderComponent from "./AudioRecorderComponent.jsx";
import EnvironmentStarter from "./EnvironmentStarter.jsx";
import {OidcProvider, OidcSecure} from "@axa-fr/react-oidc";

const configuration = {
  client_id: 'interactive.public',
  redirect_uri: window.location.origin + '/authentication/callback',
  silent_redirect_uri: window.location.origin + '/authentication/silent-callback',
  scope: 'openid profile email api offline_access',
  authority: 'https://demo.duendesoftware.com',
};

function App() {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
           return (
               <OidcProvider configuration={configuration}>
                  <AppSecure/>
               </OidcProvider>
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

const AppSecure = () => {
    return  <OidcSecure>
               <EnvironmentStarter>
                   <div className="App">
                       <AudioRecorderComponent/>
                   </div>
               </EnvironmentStarter>
           </OidcSecure>;
}

export default App
