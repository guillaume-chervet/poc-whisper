import React, { useState, useEffect } from 'react';
import BaseUrlContext from './BaseUrlContext';

const EnvironmentStarter = ({ children }) => {
  const [baseUrl, setBaseUrl] = useState('');
  const [statusData, setStatusData] = useState(null);

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
      console.log('tempBaseUrl:', tempBaseUrl);
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

  if (!baseUrl) {
    return (
      <div>
        <input
          type="text"
          placeholder="Entrez la baseUrl"
          value={baseUrl}
          onChange={(e) => setBaseUrl(e.target.value)}
        />
      </div>
    );
  }

  if (!statusData) {
    return <div>Chargement des données...</div>;
  }

  const allReady = statusData.every((item) => item.NumberReady >= 1);

  if (allReady) {
    console.log('Tous les pods sont prêts');
    console.log('baseUrl:', baseUrl);
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
        <p>Démarrage de l'environnement en cours...</p>
        <p>Pods en cours de démarrage : {startingPods}</p>
      </div>
    );
  }
};

export default EnvironmentStarter;
