import React, { useState, useCallback, useEffect } from "react";
import { 
  Stack, 
  TextArea, 
  Button, 
  Text, 
  Box, 
  SectionMessage,
  Spinner,
  Heading
} from "@forge/react";
import { createJiraIssue } from "./helper";
import { invoke } from "@forge/bridge";

// Map dollar allocation percentage to Jira priority strings based on relative ranking
const mapPriorityByRanking = (stories) => {
  if (!stories || stories.length === 0) return [];
  
  // Create array with original index and priority for sorting
  const storiesWithIndex = stories.map((story, index) => ({
    originalIndex: index,
    priority: story.priority || 0
  }));
  
  // Sort by priority (dollar allocation) in descending order
  storiesWithIndex.sort((a, b) => b.priority - a.priority);
  
  // Create a map of original index to priority based on ranking
  const priorityMap = {};
  const totalStories = stories.length;
  
  storiesWithIndex.forEach((item, rankIndex) => {
    // Distribute priorities evenly across the range based on rank position
    if (totalStories === 1) {
      priorityMap[item.originalIndex] = "Medium";
    } else {
      // Calculate the position as a percentage of the total range
      const position = rankIndex / (totalStories - 1);
      
      if (position === 0) {
        // First item (highest allocation)
        priorityMap[item.originalIndex] = "Highest";
      } else if (position === 1) {
        // Last item (lowest allocation)
        priorityMap[item.originalIndex] = "Lowest";
      } else if (position <= 0.25) {
        // Top 25% of remaining items
        priorityMap[item.originalIndex] = "High";
      } else if (position <= 0.75) {
        // Middle 50% of items
        priorityMap[item.originalIndex] = "Medium";
      } else {
        // Bottom 25% of remaining items (but not the very last)
        priorityMap[item.originalIndex] = "Low";
      }
    }
  });
  
  return priorityMap;
};

export const BacklogGenerationView = () => {
  const [requirements, setRequirements] = useState("");
  const [userStories, setUserStories] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");  const [addingToBacklog, setAddingToBacklog] = useState({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState('');
  const [pollInterval, setPollInterval] = useState(null);
  const [addingAllToBacklog, setAddingAllToBacklog] = useState(false);const clearMessages = useCallback(() => {
    setError("");
    setSuccessMessage("");
    setGenerationProgress('');
  }, []);
  
  const validateRequirements = (req) => {
    if (!req || req.trim().length < 10) {
      return "Please provide detailed project requirements (at least 10 characters)";
    }
    return null;
  };
  const handleGenerate = async () => {
    clearMessages();
    
    const validationError = validateRequirements(requirements);
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsGenerating(true);
    setIsLoading(true);
    setUserStories([]); // Clear previous results
    setGenerationProgress('Starting user story generation...');
    
    try {
      // Start generation job
      const jobResponse = await invoke("startUserStoryGeneration", { requirements });
      
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
        const status = await invoke('checkUserStoryGenerationStatus', { jobId });
        
        if (status.completed) {
          clearInterval(interval);
          setPollInterval(null);
            if (status.success && status.data) {            if (status.data.result && Array.isArray(status.data.result)) {
              // First, create the priority mapping based on relative ranking
              const priorityMap = mapPriorityByRanking(status.data.result);
                const mappedStories = status.data.result.map((story, index) => ({
                storyNumber: index + 1, // Permanent story number assigned at generation
                summary: story.user_story || '',
                description: story.description || '',
                budgetAllocation: story.priority || 0,
                priority: priorityMap[index] || "Medium",
                isChecked: false,
                addedToBacklog: false // Track if story has been added to backlog
              }));

              setUserStories(mappedStories);
              setSuccessMessage(`🎉 Successfully generated ${mappedStories.length} user stories!`);
            } else {
              setError("Received unexpected response format from the server");
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
          const baseProgress = status.progress || 'Generating user stories...';
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
  }, [pollInterval]);  const handleAddToBacklog = async (index) => {
    clearMessages();
    const story = userStories[index];

    setAddingToBacklog(prev => ({ ...prev, [index]: true }));
    
    try {
      const issueData = {
        summary: story.summary,
        description: story.description,
        priority: story.priority || "Medium",
      };

      const result = await createJiraIssue(issueData);

      if (result.success) {
        // Mark story as added to backlog instead of removing it
        setUserStories(prevStories => 
          prevStories.map((s, i) => 
            i === index ? { ...s, addedToBacklog: true } : s
          )
        );
        setSuccessMessage(`Successfully added "Story #${story.storyNumber}" to backlog!`);
      } else {
        setError(`Failed to create Jira issue: ${result.error}`);
      }    } catch (error) {
      setError('An error occurred while adding to backlog. Please try again.');    } finally {
      setAddingToBacklog(prev => ({ ...prev, [index]: false }));
    }
  };

  const handleAddAllToBacklog = async () => {
    clearMessages();
    setAddingAllToBacklog(true);
    
    try {
      const storiesToAdd = userStories.filter(story => !story.addedToBacklog);
      let successCount = 0;
      let failCount = 0;

      for (let i = 0; i < storiesToAdd.length; i++) {
        const storyIndex = userStories.findIndex(s => s === storiesToAdd[i]);
        const story = storiesToAdd[i];
        
        try {
          const issueData = {
            summary: story.summary,
            description: story.description,
            priority: story.priority || "Medium",
          };

          const result = await createJiraIssue(issueData);

          if (result.success) {
            // Mark story as added to backlog
            setUserStories(prevStories => 
              prevStories.map((s, idx) => 
                idx === storyIndex ? { ...s, addedToBacklog: true } : s
              )
            );
            successCount++;
          } else {
            failCount++;
          }
        } catch (error) {
          failCount++;
        }
      }

      if (successCount > 0 && failCount === 0) {
        setSuccessMessage(`🎉 Successfully added all ${successCount} user stories to backlog!`);
      } else if (successCount > 0 && failCount > 0) {
        setSuccessMessage(`Added ${successCount} stories to backlog. ${failCount} failed - please try again for those.`);
      } else {
        setError('Failed to add stories to backlog. Please try again.');
      }
    } catch (error) {
      setError('An error occurred while adding stories to backlog. Please try again.');
    } finally {
      setAddingAllToBacklog(false);
    }
  };return (
    <Box
      maxWidth="1200px"
      margin="0 auto"
      padding="space.400"
      minHeight="100vh"
      backgroundColor="color.background.neutral.subtle"
    >
      <Stack space="space.300">        {/* Header */}

        {/* Main Content Grid */}
        <Stack space="space.200" direction={userStories.length > 0 ? "horizontal" : "vertical"}>
          {/* Left Column - Input Section */}
          <Box>
            <Stack space="space.200">              {/* Error Message */}
              {error && (
                <SectionMessage appearance="error">
                  <Box>
                    <Text>{error}</Text>
                  </Box>
                </SectionMessage>
              )}

              {/* Success Message */}
              {successMessage && (
                <SectionMessage appearance="success">
                  <Text>{successMessage}</Text>
                </SectionMessage>
              )}              {/* Input Section */}
              <Box
                padding="space.300"
                backgroundColor="color.background.neutral"
                borderRadius="space.200"
              >
                <Stack space="space.200">
                  <Box display="flex" alignItems="center">
                    <Text weight="bold" size="large">Project Requirements</Text>
                  </Box>
                  <TextArea
                    placeholder="Example: 'Build an e-commerce platform for small businesses with inventory management, payment processing, customer accounts, and order tracking. Must integrate with existing accounting software and support mobile devices.'"
                    value={requirements}
                    onChange={(e) => setRequirements(e.target.value)}
                    isInvalid={!!error && error.includes("requirements")}
                  />
                  <Box
                    padding="space.100"
                    backgroundColor="color.background.input"
                    borderRadius="border.radius"
                  >
                    <Text size="small" color="color.text.subtle">
                      💡 More detailed requirements = better user stories
                    </Text>
                  </Box>
                </Stack>
              </Box>
                <Button 
                appearance="primary" 
                onClick={handleGenerate} 
                isDisabled={isLoading || !requirements.trim()}
                iconAfter={isLoading ? <Spinner size="small" /> : undefined}
                size="large"
              >
                {isLoading ? "🤖 Generating User Stories..." : "✨ Generate User Stories"}
              </Button>              {/* Progress Message */}
              {isGenerating && generationProgress && (
                <Box
                  padding="space.200"
                  backgroundColor="color.background.information.subtlest"
                  borderRadius="space.100"
                  textAlign="center"
                >
                  <Stack space="space.100">
                    <Text color="color.text.information" size="small">
                      {generationProgress}
                    </Text>
                    {generationProgress.includes('Generation job started') && (
                      <Text color="color.text.subtle" size="small">
                        This may take a few minutes for complex requirements...
                      </Text>
                    )}
                  </Stack>
                </Box>
              )}{/* Stats Section */}
            </Stack>
          </Box>          {/* Right Column - User Stories Section */}
          {userStories.length > 0 && (
            <Box>
              <Stack space="space.100">                <Box
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                  padding="space.200"
                  backgroundColor="color.background.accent.blue.subtlest"
                  borderRadius="space.100"
                >
                  <Heading size="large">📋 Generated User Stories</Heading>
                  <Button
                    appearance="primary"
                    size="medium"
                    onClick={handleAddAllToBacklog}
                    isDisabled={addingAllToBacklog || userStories.every(story => story.addedToBacklog)}
                    iconAfter={addingAllToBacklog ? <Spinner size="small" /> : undefined}
                  >
                    {addingAllToBacklog 
                      ? "🚀 Adding All..." 
                      : userStories.every(story => story.addedToBacklog)
                        ? "✅ All Added"
                        : "📥 Add All to Backlog"
                    }
                  </Button>
                </Box>
                
                <Stack space="space.200">                  {userStories.map((story, index) => (
                    <Box
                      key={index}
                      borderColor="color.border"
                      borderWidth="border.width.outline"
                      borderRadius="space.200"
                      padding="space.300"
                      backgroundColor="color.background.accent.blue.subtlest"
                    >
                      <Stack space="space.200">                        {/* Story Header */}
                        <Box
                          display="flex"
                          justifyContent="space-between"
                          alignItems="center"
                          paddingBottom="space.100"
                        >
                          <Text weight="bold" color="color.text.subtle">Story #{story.storyNumber}</Text>
                        </Box>                        {/* Story Content */}
                        <Box marginBottom="space.200">
                          <Text weight="bold" size="medium" color="color.text.accent.blue">
                            📝 User Story
                          </Text>
                          <Box
                            padding="space.200"
                            backgroundColor="color.background.input"
                            borderRadius="border.radius"
                            marginTop="space.100"
                          >
                            <Text>{story.summary}</Text>
                          </Box>
                        </Box>

                        <Box marginBottom="space.200">
                          <Text weight="bold" size="medium" color="color.text.accent.blue">
                            📄 Description
                          </Text>
                          <Box
                            padding="space.200"
                            backgroundColor="color.background.input"
                            borderRadius="border.radius"
                            marginTop="space.100"
                          >
                            <Text>{story.description}</Text>
                          </Box>
                        </Box>                        <Box marginBottom="space.200">
                          <Text weight="bold" size="medium" color="color.text.accent.blue">
                            🎯 Priority
                          </Text>
                          <Box
                            padding="space.200"
                            backgroundColor="color.background.input"
                            borderRadius="border.radius"
                            marginTop="space.100"
                          >
                            <Text> {story.priority} priority</Text>
                          </Box>
                        </Box>
                          {/* Action Button */}
                        <Box
                          display="flex"
                          justifyContent="center"
                          marginTop="space.200"
                          paddingTop="space.200"
                        >                          <Button 
                            appearance={story.addedToBacklog ? "subtle" : "primary"}
                            size="large"
                            isDisabled={addingToBacklog[index] || story.addedToBacklog}
                            onClick={() => handleAddToBacklog(index)}
                            iconAfter={addingToBacklog[index] ? <Spinner size="small" /> : undefined}
                          >
                            {story.addedToBacklog 
                              ? "✅ Added to Backlog" 
                              : addingToBacklog[index] 
                                ? "🚀 Adding to Backlog..." 
                                : "Add to Jira Backlog"
                            }
                          </Button>
                        </Box>
                      </Stack>                    </Box>
                  ))}
                </Stack>
              </Stack>
            </Box>
          )}
        </Stack>

        {/* Empty State */}
        {!isLoading && userStories.length === 0 && requirements && (
          <Box
            textAlign="center"
            padding="space.500"
            backgroundColor="color.background.neutral"
            borderRadius="space.200"
          >
            <Text size="large" color="color.text.subtle">
              🎯 Ready to generate user stories!
            </Text>
            <Text color="color.text.subtle">
              Click "Generate User Stories" to transform your requirements into actionable user stories.
            </Text>
          </Box>
        )}

        {/* Getting Started */}
        {!requirements && userStories.length === 0 && (
          <Box
            padding="space.400"
            backgroundColor="color.background.accent.blue.subtlest"
            borderRadius="space.200"
          >
            <Stack space="space.200">
              <Heading size="medium" color="color.text.accent.blue">🚀 Getting Started</Heading>
              <Text>Follow these steps to generate your user stories:</Text>
              
              <Stack space="space.100">
                <Text>📝 Step 1: Describe your project requirements in detail</Text>
                <Text>✨ Step 2: Click "Generate User Stories" to use AI</Text>
                <Text>✏️ Step 3: Review and edit the generated stories</Text>
                <Text>➕ Step 4: Add them to your Jira backlog</Text>
              </Stack>
            </Stack>
          </Box>
        )}
      </Stack>
    </Box>
  );
};