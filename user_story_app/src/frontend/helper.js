import { requestJira } from "@forge/bridge";

// Validate issue data before sending
const validateIssueData = (issueData) => {
  const errors = [];
  
  if (!issueData.summary || issueData.summary.trim().length === 0) {
    errors.push("Summary is required");
  }
  
  if (issueData.summary && issueData.summary.length > 255) {
    errors.push("Summary must be less than 255 characters");
  }
  
  if (!issueData.description || issueData.description.trim().length === 0) {
    errors.push("Description is required");
  }
  
  const validPriorities = ["Lowest", "Low", "Medium", "High", "Highest"];
  if (issueData.priority && !validPriorities.includes(issueData.priority)) {
    errors.push("Invalid priority value");
  }
  
  return errors;
};

export const createJiraIssue = async (issueData) => {
  try {
    // Validate input data
    const validationErrors = validateIssueData(issueData);
    if (validationErrors.length > 0) {
      return { 
        success: false, 
        error: `Validation failed: ${validationErrors.join(", ")}` 
      };
    }

    // Prepare the request body
    const requestBody = {
      fields: {
        project: {
          id: "10000", // Replace with your actual project ID
        },
        summary: issueData.summary.trim(),
        description: {
          content: [
            {
              content: [
                {
                  text: issueData.description.trim(),
                  type: "text",
                },
              ],
              type: "paragraph",
            },
          ],
          type: "doc",
          version: 1,
        },
        issuetype: {
          name: "Story",
        },
      },
    };

    // Add priority if provided
    if (issueData.priority) {
      requestBody.fields.priority = {
        name: issueData.priority,
      };
    }

    // Add epic if provided and not empty
    if (issueData.epic && issueData.epic.trim()) {
      // Note: You might need to adjust this based on your Jira setup
      // This assumes you have a custom field for epic link
      requestBody.fields.labels = [issueData.epic.trim()];
    }

    const response = await requestJira("/rest/api/3/issue", {
      method: "POST",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      let errorMessage = `HTTP error! status: ${response.status}`;
      
      try {
        const errorData = await response.json();
        if (errorData.errors) {
          const errorDetails = Object.entries(errorData.errors)
            .map(([field, message]) => `${field}: ${message}`)
            .join(", ");
          errorMessage = `Jira API error: ${errorDetails}`;
        } else if (errorData.errorMessages) {
          errorMessage = `Jira API error: ${errorData.errorMessages.join(", ")}`;
        }
      } catch (parseError) {
        // If we can't parse the error response, use the original HTTP error
        console.warn("Could not parse error response:", parseError);
      }
      
      throw new Error(errorMessage);
    }

    const createdIssue = await response.json();
    return { 
      success: true, 
      data: createdIssue,
      issueKey: createdIssue.key,
      issueUrl: `${createdIssue.self.split('/rest/')[0]}/browse/${createdIssue.key}`
    };
  } catch (error) {
    console.error("Error creating issue:", error);
    return { 
      success: false, 
      error: error.message || "An unexpected error occurred while creating the Jira issue"
    };
  }
};