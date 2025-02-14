import Resolver from '@forge/resolver';
import api, { route } from '@forge/api';

const url = 'https://mou3.pythonanywhere.com/run-python';
const apiKey = process.env.GROQ_API_KEY;

const resolver = new Resolver();

resolver.define('askGPT', async ({ payload }) => {
  
  try {
    const response = await api.fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({body:payload.requirements}),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error calling API:', error);
    return 'Failed to generate user stories. Please try again.';
  }
  
});

// **Export the run function from your resolver**
export const handler = resolver.getDefinitions();
