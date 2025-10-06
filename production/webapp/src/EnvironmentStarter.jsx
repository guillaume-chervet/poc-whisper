import React, { useState } from 'react';
import BaseUrlContext from './BaseUrlContext';
import PlanetSaver from "./PlanetSaver.jsx";

const EnvironmentStarter = ({ children }) => {
  const [baseUrl, setBaseUrl] = useState('http://localhost:5020/function/api');

  if (!baseUrl) {
    return (
      <div>
        <input
          type="text"
          placeholder="Enter baseUrl"
          value={baseUrl}
          onChange={(e) => setBaseUrl(e.target.value)}
        />
      </div>
    );
  }

  let tempUrl = baseUrl;
  if (tempUrl.endsWith('/')) tempUrl = tempUrl.slice(0, -1);
  if (tempUrl.endsWith('/function/api')) {
    tempUrl = tempUrl.replace('/function/api', '');
  }
  
  // Une fois le premier démarrage terminé, afficher les enfants
  return <><BaseUrlContext.Provider value={baseUrl}>
    <PlanetSaver baseUrl={tempUrl}>{children}</PlanetSaver> 
  </BaseUrlContext.Provider></>;
};

export default EnvironmentStarter;
