import Resolver from '@forge/resolver';
import api, { route, storage } from '@forge/api';

const url = 'https://mou3.pythonanywhere.com/generate_and_priortize_us';

const resolver = new Resolver();

resolver.define('askGPT', async ({ payload }) => {
  try {
    const response = await api.fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ body: payload.requirements }),
    });

    const textResponse = await response.text();
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} - ${response.statusText}`);
    }

    try {
      const jsonResponse = JSON.parse(textResponse);
      return jsonResponse;
    } catch (jsonError) {
      throw new Error('Invalid response format received');
    }
  } catch (error) {
    return { error: 'Failed to generate user stories' };
  }
});

// Start async user story generation job
resolver.define('startUserStoryGeneration', async ({ payload }) => {
  try {
    const jobId = '_job_us_' + Math.random().toString(36).substr(2, 9) + Date.now();
    
    // Store job status
    await storage.set(`job_${jobId}`, {
      status: 'started',
      requirements: payload.requirements,
      progress: 'Starting user story generation...',
      completed: false,
      failed: false,
      startTime: Date.now()
    });
    
    // Start async generation process
    generateUserStoriesAsync(jobId, payload.requirements);
    
    return { jobId };
  } catch (error) {
    return { error: 'Failed to start generation job' };
  }
});

// Check user story generation job status
resolver.define('checkUserStoryGenerationStatus', async ({ payload }) => {
  try {
    const jobStatus = await storage.get(`job_${payload.jobId}`);
    
    if (!jobStatus) {
      // If job not found, it might have been cleaned up - return a neutral status
      return { 
        completed: false, 
        failed: false, 
        progress: 'Job status not found, but generation may still be running...' 
      };
    }
    
    return {
      completed: jobStatus.completed,
      failed: jobStatus.failed,
      success: jobStatus.success,
      data: jobStatus.data,
      error: jobStatus.error,
      progress: jobStatus.progress
    };
  } catch (error) {
    // Don't fail completely - just return a status that allows polling to continue
    return { 
      completed: false, 
      failed: false, 
      progress: 'Checking job status...' 
    };
  }
});

// Async user story generation function
const generateUserStoriesAsync = async (jobId, requirements) => {
  // Don't use try-catch here to avoid blocking the initial response
  // Update job status to processing
  await storage.set(`job_${jobId}`, {
    status: 'processing',
    requirements,
    progress: 'Generating user stories...',
    completed: false,
    failed: false,
    startTime: Date.now()
  });

  // Use setImmediate to ensure this runs asynchronously and doesn't block
  setImmediate(async () => {
    await makeApiCallWithRetry(jobId, requirements);
  });
};

// Make API call with retry mechanism to handle long-running requests
const makeApiCallWithRetry = async (jobId, requirements, attempt = 1) => {
  const maxAttempts = 5; // Increase max attempts
  
  try {
    // Update progress for each attempt
    await storage.set(`job_${jobId}`, {
      status: 'processing',
      requirements,
      progress: attempt === 1 ? 'Connecting to AI service...' : `Retrying connection... (attempt ${attempt}/${maxAttempts})`,
      completed: false,
      failed: false,
      startTime: Date.now()
    });

    // Make API call with extended timeout
    const response = await api.fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ body: requirements }),
    });

    const textResponse = await response.text();
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} - ${textResponse}`);
    }

    const jsonResponse = JSON.parse(textResponse);

    // Update job status to completed
    await storage.set(`job_${jobId}`, {
      status: 'completed',
      requirements,
      progress: 'User story generation completed successfully',
      completed: true,
      failed: false,
      success: true,
      data: jsonResponse,
      startTime: Date.now()
    });

    // Clean up job after 24 hours
    setTimeout(async () => {
      try {
        await storage.delete(`job_${jobId}`);
      } catch (e) {
        // Silently ignore cleanup errors
      }
    }, 24 * 60 * 60 * 1000);

  } catch (error) {
    if (attempt < maxAttempts) {
      // Wait longer between retries for large requests
      const delay = Math.min(5000 * attempt, 15000); // 5s, 10s, 15s, 15s, 15s
      
      await storage.set(`job_${jobId}`, {
        status: 'processing',
        requirements,
        progress: `Large request processing... retrying in ${delay/1000}s (attempt ${attempt}/${maxAttempts})`,
        completed: false,
        failed: false,
        startTime: Date.now()
      });
      
      setTimeout(async () => {
        await makeApiCallWithRetry(jobId, requirements, attempt + 1);
      }, delay);
      
    } else {
      // Final failure after all attempts
      await storage.set(`job_${jobId}`, {
        status: 'failed',
        requirements,
        progress: 'Generation failed - request may be too large or service temporarily unavailable',
        completed: true,
        failed: true,
        success: false,
        error: 'Failed to generate user stories after multiple attempts',
        startTime: Date.now()
      });
    }
  }
};

// **Export the run function from your resolver**
export const handler = resolver.getDefinitions();
