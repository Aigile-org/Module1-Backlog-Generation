import logging
from groq import Groq
import os
import re
logger = logging.getLogger(__name__)

API_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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"
]

async def send_to_llm(prompt, type_=None):
    """
    Sends a prompt to the Groq LLM API, handling rate limits by cycling through a list of API keys.
    """
    model = "llama3-70b-8192"
    
    # Iterate through the list of available API keys
    for i, api_key in enumerate(API_KEYS):
        try:
            print(f"Attempting API call with key #{i + 1}...")
            client = Groq(api_key=api_key)
            
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model= model,
                stream=False,
            )
            
            # If the request is successful, return the output
            print(f"Success with key #{i + 1}.")
            output = response.choices[0].message.content
            return output
            
        except RateLimitError as e:
            # This block catches the specific rate limit error
            print(f"Rate limit reached for key #{i + 1}. Error details: {e.body.get('error', {}).get('message')}")
            if i < len(API_KEYS) - 1:
                print("Switching to the next API key.")
            else:
                print("All API keys have been rate-limited.")
            # The loop will continue to the next key
            
        except Exception as e:
            # Catch other potential exceptions (e.g., authentication, connection errors)
            print(f"An unexpected error occurred with key #{i + 1}: {e}")
            if i < len(API_KEYS) - 1:
                print("Trying next key...")
            else:
                print("All keys failed.")
                
    # If the loop completes without a successful call, return None
    print("Could not get a response from the API. All keys are likely exhausted.")
    return None
#*************100 Dollar**********
def construct_batch_100_dollar_prompt(data, dev_response, qa_response, po_response):
    stories_formatted = '\n'.join([
        f"- Story ID {index + 1}: '{story['user_story']}' {story['epic']} {story['description']}"
        for index, story in enumerate(data['stories'])
    ])

    prompt_file_path = os.path.join(os.path.dirname(__file__), "batch_100_dollar_prompt.txt")
    with open(prompt_file_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    print("Prompt template loaded successfully.")
    print("Stories formatted:", stories_formatted)
    print("QA response direct:", qa_response)        
    print("Dev response direct:", dev_response)
    print("PO response direct:", po_response)
    prompt = prompt_template.format(
        stories_formatted=stories_formatted,
        qa_response_direct=qa_response,
        dev_response_direct=dev_response,
        po_response_direct=po_response
    )
    print("Batch 100 Dollar prompt content:", prompt)
    return prompt

async def engage_agents_in_prioritization(prompt, stories, max_retries=20 ):
    logger.info(f"Engaging agents in prioritization with prompt: {prompt}")
    for attempt in range(max_retries):
        try:
            final_response = await send_to_llm(prompt,"100-dollar")
            dollar_distribution = parse_100_dollar_response(final_response)

            if not dollar_distribution:
                logger.error(f"Failed to parse dollar distribution: {final_response}")
                continue

            logger.info(f"Dollar Response: {dollar_distribution}")

            enriched_stories = enrich_stories_with_dollar_distribution(stories, dollar_distribution)
            # await websocket.send_json({"agentType": "Final Prioritization", "message": {"stories": enriched_stories}})
            return enriched_stories

        except Exception as e:
            logger.error(f"Error during prioritization attempt {attempt + 1}: {str(e)}")
        logger.info(f"Retrying prioritization... ({attempt + 1}/{max_retries})")

    raise Exception("Failed to get valid response from agents after multiple attempts")

def parse_100_dollar_response(response_text):
    pattern = re.compile(r"- Story ID (\d+): .*?(\d+) dollars")
    dollar_distribution = []

    for match in pattern.finditer(response_text):
        story_id, dollars = match.groups()
        dollar_distribution.append({
            'story_id': int(story_id),
            'dollars': int(dollars)
        })

    return dollar_distribution

# Adding dollar allocation to original stories
def enrich_stories_with_dollar_distribution(original_stories, dollar_distribution):
    dollar_dict = {dist['story_id']: dist['dollars'] for dist in dollar_distribution}

    enriched_stories = []
    for story in original_stories:
        story_id = story['key'] + 1
        story['dollar_allocation'] = dollar_dict.get(story_id, 0)
        enriched_stories.append(story)

    # Sort the enriched stories by dollar_allocation in descending order
    enriched_stories.sort(key=lambda x: x['dollar_allocation'], reverse=True)

    return enriched_stories
