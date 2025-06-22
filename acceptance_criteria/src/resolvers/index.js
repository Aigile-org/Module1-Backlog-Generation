import Resolver from '@forge/resolver';
import api, { storage } from '@forge/api';

const url = 'https://mou3.pythonanywhere.com/generate-single-ac';
const resolver = new Resolver();

const getListKeyFromContext = (context) => {
  // Use the issue key from the context to ensure unique storage per issue
  return context.extension?.issue?.key || context.localId?.split('/').pop();
};

const getAll = async (listId) => {
  return await storage.get(listId) || [];
};

resolver.define('getAcceptanceCriteria', async ({ payload, context }) => {
  try {
    const response = await api.fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ body: payload.userStory }),
    });

    const textResponse = await response.text();
    if (!response.ok) throw new Error(`API Error: ${response.status} - ${textResponse}`);

    const generatedACs = JSON.parse(textResponse);
    
    // Use issue key for unique storage per issue
    const listId = payload.issueKey || getListKeyFromContext(context);
    const storedACs = await getAll(listId);

    const newACs = generatedACs.result.map(ac => ({ id: '_' + Math.random().toString(36).substr(2, 9), text: ac, completed: false }));
    await storage.set(listId, [...storedACs, ...newACs]);

    return newACs;
  } catch (error) {
    return { error: 'Failed to generate acceptance criteria' };
  }
});
resolver.define('storeACs', async ({ payload, context }) => {
  try {
    // Use issue key for unique storage per issue
    const listId = payload.issueKey || getListKeyFromContext(context);
    
    // Replace the old ACs with the new ones
    await storage.set(listId, payload.newACs);

    return payload.newACs;
  } catch (error) {
    return { error: 'Failed to store acceptance criteria' };
  }
});


resolver.define('get-all', async ({ payload, context }) => {
  // Use issue key for unique storage per issue
  const listId = payload?.issueKey || getListKeyFromContext(context);
  return getAll(listId);
});

resolver.define('update', async ({ payload, context }) => {
  // Use issue key for unique storage per issue
  const listId = payload.issueKey || getListKeyFromContext(context);
  let records = await getAll(listId);

  records = records.map(item => (item.id === payload.id ? { ...item, ...payload } : item));

  await storage.set(listId, records);
  return payload;
});

resolver.define('delete', async ({ payload, context }) => {
  // Use issue key for unique storage per issue
  const listId = payload.issueKey || getListKeyFromContext(context);
  let records = await getAll(listId);

  records = records.filter(item => item.id !== payload.id);

  await storage.set(listId, records);
  return { message: 'deleted' };
});

resolver.define('mark-generated', async ({ payload, context }) => {
  try {
    // Use issue key for unique storage per issue
    const listId = payload.issueKey || getListKeyFromContext(context);
    
    // Store a flag to indicate that the ACs have been generated
    const generatedFlag = { generated: true };
    
    await storage.set(listId + "-generated", generatedFlag);
    
    return { success: true };
  } catch (error) {
    return { error: 'Failed to mark as generated' };
  }
});

resolver.define('is-generated', async ({ payload, context }) => {
  try {
    // Use issue key for unique storage per issue
    const listId = payload?.issueKey || getListKeyFromContext(context);
    const generatedFlag = await storage.get(listId + "-generated");
    return generatedFlag ? generatedFlag.generated : false;
  } catch (error) {
    return false;
  }
});

// Start async generation job
resolver.define('startGeneration', async ({ payload, context }) => {
  try {
    const jobId = '_job_' + Math.random().toString(36).substr(2, 9) + Date.now();
    const listId = payload.issueKey || getListKeyFromContext(context);
    
    // Store job status
    await storage.set(`job_${jobId}`, {
      status: 'started',
      issueKey: listId,
      userStory: payload.userStory,
      progress: 'Starting generation...',
      completed: false,
      failed: false,
      startTime: Date.now()
    });
    
    // Start async generation process
    generateACsAsync(jobId, payload.userStory, listId);
    
    return { jobId };
  } catch (error) {
    return { error: 'Failed to start generation job' };
  }
});

// Check generation job status
resolver.define('checkGenerationStatus', async ({ payload }) => {
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

// Async generation function
const generateACsAsync = async (jobId, userStory, listId) => {
  try {
    // Update job status to processing
    await storage.set(`job_${jobId}`, {
      status: 'processing',
      issueKey: listId,
      userStory,
      progress: 'Generating acceptance criteria...',
      completed: false,
      failed: false,
      startTime: Date.now()
    });

    // Make API call
    const response = await api.fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ body: userStory }),
    });

    const textResponse = await response.text();
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} - ${textResponse}`);
    }

    const generatedACs = JSON.parse(textResponse);
    const storedACs = await getAll(listId);

    const newACs = generatedACs.result.map(ac => ({ 
      id: '_' + Math.random().toString(36).substr(2, 9), 
      text: ac, 
      completed: false 
    }));

    // Store the new ACs
    await storage.set(listId, [...storedACs, ...newACs]);

    // Update job status to completed
    await storage.set(`job_${jobId}`, {
      status: 'completed',
      issueKey: listId,
      userStory,
      progress: 'Generation completed successfully',
      completed: true,
      failed: false,
      success: true,
      data: newACs,
      startTime: Date.now()
    });

    // Clean up job after 24 hours instead of 5 minutes for long-running jobs
    setTimeout(async () => {
      try {
        await storage.delete(`job_${jobId}`);
      } catch (e) {
        // Silently ignore cleanup errors
      }
    }, 24 * 60 * 60 * 1000); // 24 hours

  } catch (error) {
    // Update job status to failed
    await storage.set(`job_${jobId}`, {
      status: 'failed',
      issueKey: listId,
      userStory,
      progress: 'Generation failed',
      completed: true,
      failed: true,
      success: false,
      error: 'Failed to generate acceptance criteria',
      startTime: Date.now()
    });
  }
};

export const handler = resolver.getDefinitions();
