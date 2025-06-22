import Resolver from '@forge/resolver';
import api, { storage } from '@forge/api';

const url = 'https://mou3.pythonanywhere.com/generate-single-ac';
const resolver = new Resolver();

const getListKeyFromContext = (context) => {
  const { localId: id } = context;
  return id.split('/')[id.split('/').length - 1];
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
    const listId = getListKeyFromContext(context);
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
    const listId = getListKeyFromContext(context);
    
    // Replace the old ACs with the new ones
    await storage.set(listId, payload.newACs);

    return payload.newACs;
  } catch (error) {
    return { error: 'Failed to store acceptance criteria' };
  }
});


resolver.define('get-all', async ({ context }) => {
  return getAll(getListKeyFromContext(context));
});

resolver.define('update', async ({ payload, context }) => {
  const listId = getListKeyFromContext(context);
  let records = await getAll(listId);

  records = records.map(item => (item.id === payload.id ? { ...item, ...payload } : item));

  await storage.set(listId, records);
  return payload;
});

resolver.define('delete', async ({ payload, context }) => {
  const listId = getListKeyFromContext(context);
  let records = await getAll(listId);

  records = records.filter(item => item.id !== payload.id);

  await storage.set(listId, records);
  return { message: 'deleted' };
});

resolver.define('mark-generated', async ({ payload, context }) => {
  try {
    const listId = getListKeyFromContext(context);
    
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
    const listId = getListKeyFromContext(context);
    const generatedFlag = await storage.get(listId + "-generated");
    return generatedFlag ? generatedFlag.generated : false;
  } catch (error) {
    return false;
  }
});


export const handler = resolver.getDefinitions();
