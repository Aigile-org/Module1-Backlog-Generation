import React from 'react';
import ForgeReconciler, { 
  Text, 
  useProductContext, 
  LoadingButton, 
  Box, 
  Stack,
  SectionMessage 
} from '@forge/react';
import { BacklogGenerationView } from './BacklogGenerationView';

const App = () => {
  const context = useProductContext();
    if (!context) {
    return (
      <Box padding="space.400">
        <Stack space="space.200">
          <LoadingButton isLoading={true} size="large">
            Loading application...
          </LoadingButton>
        </Stack>
      </Box>
    );
  }

  // Add error boundary for context issues
  try {
    return <BacklogGenerationView />;  } catch (error) {
    return (
      <Box padding="space.300">
        <SectionMessage appearance="error">
          <Text>
            An error occurred while loading the application. Please refresh and try again.
          </Text>
        </SectionMessage>
      </Box>
    );
  }
};

ForgeReconciler.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
