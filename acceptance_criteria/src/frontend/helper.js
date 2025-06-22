import { requestJira } from "@forge/bridge";


export const getIssueSummary = async (issueKey) => {
  try {
    const response = await requestJira(`/rest/api/2/issue/${issueKey}`, {
      method: "GET",
      headers: {
        "Accept": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const issueData = await response.json();
    return { success: true, summary: issueData.fields.summary };
  } catch (error) {
    console.error("Error fetching issue summary:", error);
    return { success: false, error: error.message };
  }
};

