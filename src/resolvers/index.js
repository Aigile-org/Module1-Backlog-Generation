import Resolver from '@forge/resolver';
import api, { route } from '@forge/api';

const url = 'https://api.groq.com/openai/v1/chat/completions';
const apiKey = process.env.GROQ_API_KEY;

const resolver = new Resolver();

resolver.define('askGPT', async ({ payload }) => {
  const requestBody = {
    messages: [
      {
        role: 'system',
        content: 'You are a helpful assistant that generates user stories based on project requirements.',
      },
      {
        role: 'user',
        content: `Generate user stories for the following requirements: ${payload.requirements}`,
      },
    ],
    model: 'llama-3.3-70b-versatile',
    stream: false,
  };

  try {
    const response = await api.fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    const data = await response.json();
    return data.choices[0].message.content;
  } catch (error) {
    console.error('Error calling Groq API:', error);
    return 'Failed to generate user stories. Please try again.';
  }
});

// **Export the run function from your resolver**
export const handler = resolver.getDefinitions();
