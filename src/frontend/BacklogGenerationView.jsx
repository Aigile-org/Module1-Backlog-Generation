import React, { useState } from "react";
import { Stack, TextArea, Button, Text } from "@forge/react";
import { invoke } from "@forge/bridge"; // Use Forge bridge to communicate with backend

export const BacklogGenerationView = () => {
  const [requirements, setRequirements] = useState("");
  const [userStories, setUserStories] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleGenerate = async () => {
    if (!requirements.trim()) {
      setUserStories("Please enter project requirements.");
      return;
    }

    setIsLoading(true);
    try {
      const generatedStories = await invoke("askGPT", { requirements });
      setUserStories(generatedStories);
    } catch (error) {
      setUserStories("An error occurred while generating user stories.");
      console.log(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Stack space="space.200">
      <TextArea
        label="Project Requirements"
        placeholder="Enter project requirements here..."
        value={requirements}
        onChange={(e) => setRequirements(e.target.value)}
      />
      <Button appearance="primary" onClick={handleGenerate} disabled={isLoading}>
        {isLoading ? "Generating..." : "Generate User Stories"}
      </Button>
      {userStories && <Text>{userStories}</Text>}
    </Stack>
  );
};
