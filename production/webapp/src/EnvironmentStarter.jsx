import React, { useState, useEffect } from 'react';
import BaseUrlContext from './BaseUrlContext';

const EnvironmentStarter = ({ children }) => {
  const [baseUrl, setBaseUrl] = useState('');
  const [statusData, setStatusData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let intervalId;

    if (baseUrl) {
      let tempBaseUrl = baseUrl;
      if(baseUrl.endsWith('/')) {
        tempBaseUrl = baseUrl.slice(0, -1);
      }
      if(baseUrl.endsWith('/function/api')) {
        tempBaseUrl = tempBaseUrl.replace('/function/api', '');
      }
      const fetchData = async () => {
        try {
          const response = await fetch(`${tempBaseUrl}/status-functions`);
          const data = await response.json();
          setStatusData(data);

          // Pour chaque élément, si NumberReady est 0, appeler /wake-function/<Name>
          data.forEach(async (item) => {
            if (item.NumberReady === 0) {
              await fetch(`${tempBaseUrl}/wake-function/${item.Name}`, {
                method: 'POST',
              });
            }
          });
        } catch (error) {
          console.error('Erreur lors de la récupération des données:', error);
          setError(error.message);
        }
      };

      // Appel initial
      fetchData();

      // Mise en place de l'intervalle toutes les 5 secondes
      intervalId = setInterval(fetchData, 5000);

      // Nettoyage de l'intervalle lors du démontage ou du changement de baseUrl
      return () => clearInterval(intervalId);
    }

    // Nettoyage si baseUrl est vide
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [baseUrl]);


  if(error) {
    return <div>Error while retrieving data: {error}</div>;
  }

  if (!baseUrl) {
    return (
      <div>
        <input
          type="text"
          placeholder="Enter the baseUrl"
          value={baseUrl}
          onChange={(e) => setBaseUrl(e.target.value)}
        />
      </div>
    );
  }

  if (!statusData) {
    return <div>Loading data...</div>;
  }

  const allReady = statusData.every((item) => item.NumberReady >= 1);

  if (allReady) {
    return (
      <BaseUrlContext.Provider value={baseUrl}>
        {children}
      </BaseUrlContext.Provider>
    );
  } else {
    const startingPods = statusData
      .filter((item) => item.NumberReady === 0)
      .map((item) => item.Name)
      .join(', ');

    return (
      <div>
        <p>Starting the environment in progress...</p>
        <p>Pods being started: {startingPods}</p>
      </div>
    );
  }
};

export default EnvironmentStarter;
