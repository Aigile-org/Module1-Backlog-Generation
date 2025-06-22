import React, { useState, useCallback } from "react";
import { 
  Stack, 
  TextArea, 
  Button, 
  Text, 
  Box, 
  InlineEdit, 
  Textfield,
  SectionMessage,
  Spinner,
  Heading,
  Select
} from "@forge/react";
import { createJiraIssue } from "./helper";
import { invoke } from "@forge/bridge";

const InlineEditField = ({ label, value, onChange, type = "text" }) => {
  return (
    <Box marginBottom="space.100">
      <InlineEdit
        defaultValue={value}
        label={label}
        editView={({ errorMessage, ...fieldProps }) => (
          <Textfield 
            {...fieldProps} 
            autoFocus 
            type={type}
            placeholder={`Enter ${label.toLowerCase()}...`}
          />
        )}
        readView={() => (
          <Box
            padding="space.075"
            backgroundColor="color.background.input"
            borderRadius="border.radius"
            minHeight="32px"
            display="flex"
            alignItems="center"
          >
            <Text>
              {value || `Click to edit ${label.toLowerCase()}`}
            </Text>
          </Box>
        )}
        onConfirm={(value) => onChange(value)}
      />
    </Box>
  );
};

const PrioritySelect = ({ value, onChange }) => {
  const priorityOptions = [
    { label: "Highest", value: "Highest" },
    { label: "High", value: "High" },
    { label: "Medium", value: "Medium" },
    { label: "Low", value: "Low" },
    { label: "Lowest", value: "Lowest" }
  ];

  return (
    <Box marginBottom="space.100">
      <Text weight="medium" size="small" color="color.text.subtle" marginBottom="space.050">
        🎯 Priority
      </Text>
      <Select
        options={priorityOptions}
        value={priorityOptions.find(option => option.value === value)}
        onChange={(selectedOption) => onChange(selectedOption.value)}
        placeholder="Select priority..."
      />
    </Box>
  );
};

// Map priority number to Jira priority strings
const mapPriority = (priorityNumber, totalStories) => {
  if (totalStories === 0) return "Medium";
  
  // Priority number from API (higher numbers = higher priority)
  const priority = priorityNumber || 0;

  if (priority >= 15) {
    return "Highest";
  } else if (priority >= 12) {
    return "High"; 
  } else if (priority >= 8) {
    return "Medium";
  } else if (priority >= 5) {
    return "Low";
  } else {
    return "Lowest";
  }
};

export const BacklogGenerationView = () => {
  const [requirements, setRequirements] = useState("");
  const [userStories, setUserStories] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [addingToBacklog, setAddingToBacklog] = useState({});

  const clearMessages = useCallback(() => {
    setError("");
    setSuccessMessage("");
  }, []);
  const updateUserStory = useCallback((index, field, value) => {
    setUserStories(prevStories => 
      prevStories.map((story, i) => 
        i === index 
          ? { ...story, [field]: value }
          : story
      )
    );
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

    setIsLoading(true);
    setUserStories([]); // Clear previous results
    
    try {
      console.log('Generating user stories...');
      const response = await invoke("askGPT", { requirements });      if (response.error) {
        setError(`Failed to generate user stories: ${response.error}`);
        return;
      }      if (response.result && Array.isArray(response.result)) {
        const mappedStories = response.result.map((story, index) => ({
          id: index + 1, // Permanent ID that won't change
          summary: story.user_story || '',
          description: story.description || '',
          priority: mapPriority(story.priority || 0, response.result.length),
          isChecked: false
        }));setUserStories(mappedStories);
        setSuccessMessage(`🎉 Successfully generated ${mappedStories.length} user stories!`);
      } else {
        setError("Received unexpected response format from the server");
      }    } catch (error) {
      console.error("Error generating user stories:", error);
      
      // Handle different types of errors gracefully
      let errorMessage = error.message || error.toString() || 'Unknown error occurred';
      
      // Simplify error messages for users
      if (errorMessage.includes('Task timed out') || errorMessage.includes('timed out')) {
        errorMessage = 'The AI service is currently busy processing your request. Please try again.';
      } else if (errorMessage.includes('Network Error') || errorMessage.includes('fetch')) {
        errorMessage = 'Unable to connect to the AI service. Please check your connection and try again.';
      } else if (errorMessage.includes('invoking the function')) {
        errorMessage = 'The AI service is currently unavailable. Please try again in a moment.';
      }
      
      setError(`An error occurred while generating user stories: ${errorMessage}`);
    }finally {
      setIsLoading(false);
    }
  };
    const handleAddToBacklog = async (index) => {
    clearMessages();
    const story = userStories[index];
    
    if (!story.summary || !story.description) {
      setError("Please ensure the user story has both a summary and description before adding to backlog");
      return;
    }

    setAddingToBacklog(prev => ({ ...prev, [index]: true }));
      try {
      const issueData = {
        summary: story.summary,
        description: story.description,
        priority: story.priority || "Medium",
      };

      const result = await createJiraIssue(issueData);

      if (result.success) {
        setUserStories(prevStories => prevStories.filter((_, i) => i !== index));
        setSuccessMessage(`Successfully added "${story.summary}" to backlog!`);
      } else {
        setError(`Failed to create Jira issue: ${result.error}`);
      }
    } catch (error) {
      console.error("Error adding to backlog:", error);
      setError(`An error occurred while adding to backlog: ${error.message}`);
    } finally {
      setAddingToBacklog(prev => ({ ...prev, [index]: false }));
    }
  };  return (
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
                    placeholder="Example: 'Build an e-commerce platform for small businesses with inventory management, payment processing, customer accounts, and order tracking.'"
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
              </Button>              {/* Stats Section */}
            </Stack>
          </Box>          {/* Right Column - User Stories Section */}
          {userStories.length > 0 && (
            <Box>
              <Stack space="space.100">
                <Box
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                  padding="space.200"
                  backgroundColor="color.background.accent.blue.subtlest"
                  borderRadius="space.100"
                >
                  <Heading size="large">📋 Generated User Stories</Heading>

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
                          <Text weight="bold" color="color.text.subtle">Story #{story.id}</Text>
                        </Box>

                        {/* Editable Fields */}
                        <InlineEditField 
                          label="📝 User Story" 
                          value={story.summary} 
                          onChange={(newValue) => updateUserStory(index, 'summary', newValue)} 
                        />
                          <InlineEditField 
                          label="📄 Description" 
                          value={story.description} 
                          onChange={(newValue) => updateUserStory(index, 'description', newValue)} 
                        />
                        
                        <PrioritySelect
                          value={story.priority}
                          onChange={(newValue) => updateUserStory(index, 'priority', newValue)}
                        />
                          {/* Action Button */}
                        <Box
                          display="flex"
                          justifyContent="center"
                          marginTop="space.200"
                          paddingTop="space.200"
                        >
                          <Button 
                            appearance="primary"
                            size="large"
                            isDisabled={addingToBacklog[index] || !story.summary || !story.description}
                            onClick={() => handleAddToBacklog(index)}
                            iconAfter={addingToBacklog[index] ? <Spinner size="small" /> : undefined}
                          >
                            {addingToBacklog[index] ? "🚀 Adding to Backlog..." : "Add to Jira Backlog"}
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