import React, { useEffect, useState } from "react";
import ForgeReconciler, { 
  Stack, 
  Text, 
  Checkbox, 
  Spinner, 
  Button, 
  Box, 
  Heading,
  SectionMessage,
  ProgressBar,
  Badge,
  Lozenge
} from "@forge/react";
import { invoke, view } from '@forge/bridge';
import { getIssueSummary } from './helper';

const App = () => {
  const [key, setKey] = useState(null);
  const [ACs, setACs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [issueSummary, setIssueSummary] = useState('');
  const [isGenerated, setIsGenerated] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState('');
  const [pollInterval, setPollInterval] = useState(null);

  // Helper function to clear messages
  const clearMessages = () => {
    setError('');
    setSuccessMessage('');
    setGenerationProgress('');
  };

  // Calculate completion progress
  const getProgress = () => {
    if (ACs.length === 0) return 0;
    const completed = ACs.filter(ac => ac.completed).length;
    return (completed / ACs.length) * 100;
  };

  // Fetch issue key from the context
  useEffect(() => {
    const getKey = async () => {
      const context = await view.getContext();
      setKey(context.extension.issue.key);
    };

    getKey();
  }, []);

  useEffect(() => {
    if (key) {
      fetchIssueSummary(key);
      fetchStoredACs();
      checkIfGenerated();  // Check if ACs have been generated
    }
  }, [key]);

  const fetchIssueSummary = async (key) => {
    const { success, summary, error } = await getIssueSummary(key);
    if (success) {
      setIssueSummary(summary);
    } else {
      setError('Failed to load issue summary. Please refresh the page.');
    }
  };

  // Fetch stored Acceptance Criteria from the backend
  const fetchStoredACs = async () => {
    try {
      const storedACs = await invoke('get-all', { issueKey: key });
      if (!storedACs || storedACs.length === 0) {
        generateACs();
      } else {
        setACs(storedACs || []);
      }
    } catch (error) {
      setError('Failed to load existing acceptance criteria.');
    } finally {
      setIsLoading(false);
    }
  };

  // Check if Acceptance Criteria have already been generated
  const checkIfGenerated = async () => {
    try {
      const generatedFlag = await invoke('is-generated', { issueKey: key });
      setIsGenerated(generatedFlag);
    } catch (error) {
      // Silently fail for generated flag check
    }
  };

  // Generate new Acceptance Criteria based on the issue summary
  const generateACs = async () => {
    if (!issueSummary) return;

    clearMessages();
    setIsGenerating(true);
    setIsLoading(true);
    setGenerationProgress('Starting generation...');
    
    try {
      // Start generation job
      const jobResponse = await invoke('startGeneration', { 
        userStory: issueSummary, 
        issueKey: key 
      });
      
      if (jobResponse.jobId) {
        setGenerationProgress('Generation job started, checking progress...');
        // Start polling for completion
        startPolling(jobResponse.jobId);
      } else {
        setError('Failed to start generation. Please try again.');
        setIsLoading(false);
        setIsGenerating(false);
      }
    } catch (error) {
      setError('Failed to start generation. Please try again.');
      setIsLoading(false);
      setIsGenerating(false);
    }
  };

  // Start polling for job completion
  const startPolling = (jobId) => {
    let pollAttempts = 0;
    const maxPollAttempts = 1000000; // Allow up to 1 million attempts (essentially never give up)
    
    const interval = setInterval(async () => {
      try {
        pollAttempts++;
        const status = await invoke('checkGenerationStatus', { jobId, issueKey: key });
        
        if (status.completed) {
          clearInterval(interval);
          setPollInterval(null);
          
          if (status.success && status.data) {
            const newACs = status.data.filter(ac => !ACs.some(existingAC => existingAC.text === ac.text));
            
            if (newACs.length > 0) {
              setACs(newACs);
              await storeACs(newACs);
              await markAsGenerated();
              setSuccessMessage(`Successfully generated ${newACs.length} acceptance criteria!`);
              setIsGenerated(true);
            } else {
              setError('No new acceptance criteria were generated.');
            }
          } else {
            setError(status.error || 'Generation failed. Please try again.');
          }
          
          setIsLoading(false);
          setIsGenerating(false);
          setGenerationProgress('');
        } else if (status.failed) {
          clearInterval(interval);
          setPollInterval(null);
          setError(status.error || 'Generation failed. Please try again.');
          setIsLoading(false);
          setIsGenerating(false);
          setGenerationProgress('');
        } else {
          // Still in progress
          const timeElapsed = Math.floor(pollAttempts * 3 / 60); // minutes elapsed
          const baseProgress = status.progress || 'Generating acceptance criteria...';
          setGenerationProgress(`${baseProgress} (${timeElapsed} min elapsed)`);
        }
      } catch (error) {
        // Don't stop polling on network errors - just update progress to show we're retrying
        const timeElapsed = Math.floor(pollAttempts * 3 / 60);
        setGenerationProgress(`Checking status... (${timeElapsed} min elapsed, will keep trying indefinitely)`);
        
        // Only stop if we've exceeded the maximum attempts (which is basically never)
        if (pollAttempts >= maxPollAttempts) {
          clearInterval(interval);
          setPollInterval(null);
          setError('Generation monitoring stopped after maximum attempts.');
          setIsLoading(false);
          setIsGenerating(false);
          setGenerationProgress('');
        }
      }
    }, 3000); // Poll every 3 seconds
    
    setPollInterval(interval);
  };

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [pollInterval]);

  const storeACs = async (newACs) => {
    try {
      await invoke('storeACs', { newACs, issueKey: key });
    } catch (error) {
      // Silently fail for storage operations
    }
  };

  // Mark the ACs as generated in the backend
  const markAsGenerated = async () => {
    try {
      await invoke('mark-generated', { issueKey: key });
    } catch (error) {
      // Silently fail for marking operations
    }
  };

  const toggleComplete = async (id) => {
    const updatedAC = ACs.find(ac => ac.id === id);
    const newStatus = { ...updatedAC, completed: !updatedAC.completed };

    setACs(prev => {
      const updatedACs = prev.map(ac => (ac.id === id ? newStatus : ac));
      storeACs(updatedACs);
      
      // Show completion message
      const completedCount = updatedACs.filter(ac => ac.completed).length;
      if (completedCount === updatedACs.length && updatedACs.length > 0) {
        setSuccessMessage('All acceptance criteria completed!');
      } else if (newStatus.completed) {
        setSuccessMessage('Criteria marked as complete!');
      }
      
      return updatedACs;
    });
  };

  return (
    <Box padding="space.200">
      <Stack space="space.200">
        {/* Header Section */}
        <Box
          padding="space.200"
          backgroundColor="elevation.surface.raised"
          borderRadius="border.radius.100"
        >
          <Stack space="space.150">
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Heading size="medium" color="color.text.brand">
                Acceptance Criteria
              </Heading>
              {ACs.length > 0 && (
                <Lozenge 
                  appearance={getProgress() === 100 ? "success" : "inprogress"}
                  isBold
                >
                  {getProgress() === 100 ? "Complete" : "In Progress"}
                </Lozenge>
              )}
            </Box>
            
            {/* Progress Section */}
            {ACs.length > 0 && (
              <Box
                padding="space.150"
                backgroundColor="color.background.brand.subtlest"
                borderRadius="border.radius.050"
              >
                <Stack space="space.100">
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Text size="small" weight="medium" color="color.text.brand">
                      Progress
                    </Text>
                    <Text size="small" color="color.text.subtle">
                      {ACs.filter(ac => ac.completed).length}/{ACs.length}
                    </Text>
                  </Box>
                  <ProgressBar value={getProgress()} />
                </Stack>
              </Box>
            )}
          </Stack>
        </Box>

        {/* Messages Section */}
        {(error || successMessage) && (
          <Stack space="space.100">
            {error && (
              <SectionMessage appearance="error">
                <Text size="small">{error}</Text>
              </SectionMessage>
            )}

            {successMessage && (
              <SectionMessage appearance="success">
                <Text size="small">{successMessage}</Text>
              </SectionMessage>
            )}
          </Stack>
        )}

        {/* Generate Button Section */}
        {!isGenerated && !isLoading && (
          <Box
            padding="space.200"
            backgroundColor="elevation.surface.raised"
            borderRadius="border.radius.100"
            textAlign="center"
          >
            <Stack space="space.150" alignItems="center">
              <Text size="small" color="color.text.subtle">
                Generate AI-powered acceptance criteria
              </Text>
              <Button 
                onClick={generateACs} 
                appearance="primary"
                isDisabled={isGenerating}
              >
                {isGenerating ? "Generating..." : "Generate Criteria"}
              </Button>
            </Stack>
          </Box>
        )}

        {/* Loading State */}
        {isLoading && (
          <Box
            padding="space.200"
            textAlign="center"
            backgroundColor="elevation.surface.raised"
            borderRadius="border.radius.100"
          >
            <Stack space="space.150" alignItems="center">
              <Spinner size="medium" />
              <Text size="small" color="color.text.subtle">
                {generationProgress || 'Generating criteria...'}
              </Text>
              {isGenerating && (
                <Text size="small" color="color.text.subtlest">
                  This may take a few minutes. Please wait...
                </Text>
              )}
            </Stack>
          </Box>
        )}

        {/* Acceptance Criteria List */}
        {!isLoading && ACs.length > 0 && (
          <Box
            padding="space.200"
            backgroundColor="elevation.surface.raised"
            borderRadius="border.radius.100"
          >
            <Stack space="space.150">
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Text weight="medium" size="small" color="color.text.brand">
                  Criteria Checklist
                </Text>
                {isGenerated && (
                  <Button 
                    onClick={generateACs} 
                    appearance="subtle"
                    size="small"
                    isDisabled={isGenerating}
                  >
                    Regenerate
                  </Button>
                )}
              </Box>
              
              <Stack space="space.100">
                {ACs.map((ac, index) => (
                  <Box
                    key={ac.id}
                    padding="space.150"
                    backgroundColor={ac.completed ? "color.background.success.subtlest" : "elevation.surface"}
                    borderRadius="border.radius.050"
                    borderWidth="border.width"
                    borderColor={ac.completed ? "color.border.success" : "color.border.input"}
                  >
                    <Stack direction="horizontal" space="space.100" alignItems="flex-start">
                      <Checkbox 
                        isChecked={ac.completed}
                        onChange={() => toggleComplete(ac.id)}
                      />
                      <Stack space="space.050" grow="fill">
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Text 
                            weight="medium" 
                            size="small" 
                            color={ac.completed ? "color.text.success" : "color.text.brand"}
                          >
                            AC #{index + 1}
                          </Text>
                          {ac.completed && (
                            <Lozenge appearance="success">
                              Done
                            </Lozenge>
                          )}
                        </Box>
                        <Text 
                          color={ac.completed ? "color.text.success" : "color.text"}
                          size="small"
                          style={ac.completed ? { textDecoration: 'line-through', opacity: 0.7 } : {}}
                        >
                          {ac.text}
                        </Text>
                      </Stack>
                    </Stack>
                  </Box>
                ))}
              </Stack>

              {/* Summary Footer */}
              <Box
                padding="space.100"
                backgroundColor="color.background.information.subtlest"
                borderRadius="border.radius.050"
                textAlign="center"
              >
                <Text color="color.text.information" size="small">
                  Check off criteria as you implement them
                </Text>
              </Box>
            </Stack>
          </Box>
        )}

        {/* Empty State */}
        {!isLoading && !isGenerated && ACs.length === 0 && (
          <Box
            padding="space.200"
            textAlign="center"
            backgroundColor="elevation.surface.raised"
            borderRadius="border.radius.100"
          >
            <Stack space="space.150" alignItems="center">
              <Text size="medium">🎯</Text>
              <Text size="small" color="color.text.subtle">
                No acceptance criteria yet
              </Text>
              <Text size="small" color="color.text.subtlest">
                Generate criteria to define completion requirements
              </Text>
            </Stack>
          </Box>
        )}
      </Stack>
    </Box>
  );
};

ForgeReconciler.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
