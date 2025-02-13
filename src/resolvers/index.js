import Resolver from '@forge/resolver';
import api, { route } from '@forge/api';

const url = 'https://api.groq.com/openai/v1/chat/completions';
const apiKey = process.env.GROQ_API_KEY;

const resolver = new Resolver();

resolver.define('askGPT', async ({ payload }) => {
  // const requestBody = {
  //   messages: [
  //     {
  //       role: 'system',
  //       content: 'You are a helpful assistant that generates user stories based on project requirements.',
  //     },
  //     {
  //       role: 'user',
  //       content: `Generate user stories for the following requirements: ${payload.requirements}`,
  //     },
  //   ],
  //   model: 'llama-3.3-70b-versatile',
  //   stream: false,
  // };

  // try {
  //   const response = await api.fetch(url, {
  //     method: 'POST',
  //     headers: {
  //       'Content-Type': 'application/json',
  //       Authorization: `Bearer ${apiKey}`,
  //     },
  //     body: JSON.stringify(requestBody),
  //   });

  //   if (!response.ok) {
  //     throw new Error(`Error: ${response.status} - ${response.statusText}`);
  //   }

  //   const data = await response.json();
  //   return data.choices[0].message.content;
  // } catch (error) {
  //   console.error('Error calling Groq API:', error);
  //   return 'Failed to generate user stories. Please try again.';
  // }
  return new Promise((resolve, reject) => {
    const data_to_pass_in = payload.requirements;
    console.log('Data sent to python script:', data_to_pass_in);

    const python_process = spawner('python', [
        'D:/ComputerEngineering/GP/Module1-Backlog-Generation/python scripts/main/pipeline_1_generate_user_stories.py',
        data_to_pass_in
    ]);

    let outputData = '';

    python_process.stdout.on('data', (data) => {
        console.log('Data received from python script:', data.toString());
        outputData += data.toString(); // Append output data
    });

    python_process.stderr.on('data', (data) => {
        console.error('Error from python script:', data.toString());
        reject(data.toString()); // Reject the promise on error
    });

    python_process.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
        resolve(outputData.trim()); // Resolve the promise when the process exits
    });
});
});

// **Export the run function from your resolver**
export const handler = resolver.getDefinitions();
