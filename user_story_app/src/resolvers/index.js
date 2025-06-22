import Resolver from '@forge/resolver';
import api, { route } from '@forge/api';

const url = 'https://mou3.pythonanywhere.com/generate_and_priortize_us';

const resolver = new Resolver();

resolver.define('askGPT', async ({ payload }) => {
  try {
    console.log('Making request to backend with requirements:', payload.requirements?.substring(0, 100) + '...');
      const response = await api.fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ body: payload.requirements }),
    });

    console.log('Response status:', response.status);

    const textResponse = await response.text();    if (!response.ok) {
      throw new Error(`API Error: ${response.status} - ${response.statusText}\n${textResponse}`);
    }

    try {
      const jsonResponse = JSON.parse(textResponse);
      console.log('Successfully parsed JSON response');
      return jsonResponse;
    } catch (jsonError) {
      console.error('JSON parsing error:', jsonError);
      throw new Error(`Invalid JSON Response: ${textResponse}`);
    }
  } catch (error) {
    console.error('Error calling API:', error);
    return { error: error.message };
  }
});

// **Export the run function from your resolver**
export const handler = resolver.getDefinitions();
