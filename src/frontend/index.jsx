import React from 'react';
import ForgeReconciler, { Text, useProductContext, Spinner } from '@forge/react';
import { BacklogGenerationView } from './BacklogGenerationView';



const App = () => {
  const context = useProductContext();
  if (!context) {
    return <Spinner />;
  }
  return <BacklogGenerationView />;
};

ForgeReconciler.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
