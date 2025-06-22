import logging
from groq import Groq, RateLimitError
import os
import re

# creates a logger instance that is specific to this file
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

async def send_to_llm(prompt):
    """
    Sends a prompt to the Groq LLM API, handling rate limits by cycling through a list of API keys.
    """
    # llama3: This is the model family, Llama 3 from Meta AI
    # 70b: This refers to the number of parameters—70 billion parameters, which is a measure of the model's size and complexity.
    # 8192: context window size, meaning the model can consider up to 8192 "tokens"
    # context window size: total, combined limit for both the past context (input) and the future generation (output) added together. The more space input takes, the less space is left for the output
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
                # 'stream=False' means we will wait for the entire response to be generated
                # before the function continues. If 'stream=True', we would get the response
                # back in small chunks as it's being generated.
                stream=False,
            )
            
            # If the request is successful, return the output
            print(f"Success with key #{i + 1}.")
            output = response.choices[0].message.content
            return output
            
        except RateLimitError as e:
            # This block catches the specific rate limit error
            # e.body' often contains a JSON object with details
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
def construct_prompt(data, dev_response, qa_response, po_response):
    # '\n'.join(...) then takes all the strings in that list and joins them together
    # into a single string, with each story on a new line.
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
    # The .format() method injects all the provided pieces of text into the placeholders
    prompt = prompt_template.format(
        stories_formatted=stories_formatted,
        qa_response_direct=qa_response,
        dev_response_direct=dev_response,
        po_response_direct=po_response
    )
    print("100 Dollar prompt content:", prompt)
    return prompt

async def combining_agents(prompt, stories, max_retries=20):
    logger.info(f"Combining agents in prioritization with prompt: {prompt}")
    for attempt in range(max_retries):
        try:
            final_response = await send_to_llm(prompt)
            logger.info(f"Final response from LLM: {final_response}")
            dollar_distribution = parse_response(final_response)
            # If parsing failed (returned an empty list)
            if not dollar_distribution:
                logger.error(f"Failed to parse dollar distribution: {final_response}")
                continue

            logger.info(f"Dollar Response: {dollar_distribution}")

            # converts the list of dictionaries into a single dictionary 
            dollar_dict = {dist['story_id']: dist['dollars'] for dist in dollar_distribution}

            add_to_stories = []
            for story in stories:
                # The story's key is 0-indexed, but our IDs are 1-indexed.
                story_id = story['key'] + 1
                # add a new 'priority' key to each story dictionary
                story['priority'] = dollar_dict.get(story_id, 0)
                add_to_stories.append(story)

            # Sort the stories by priority in descending order
            add_to_stories.sort(key=lambda x: x['priority'], reverse=True)
            return add_to_stories

        except Exception as e:
            logger.error(f"Error during prioritization attempt {attempt + 1}: {str(e)}")
        logger.info(f"Retrying prioritization... ({attempt + 1}/{max_retries})")

    raise Exception("Failed to get valid response after multiple attempts")

def parse_response(response_text):
    # captures one or more digits (\d+) for the ID.
    # .*?: A non-greedy match for any characters in between. We use non-greedy (?) so it doesn't
    #  accidentally take the numbers we want to capture next
    # (\d+): Captures the dollar amount (one or more digits) followed by the word "dollars"
    pattern = re.compile(r"- Story ID (\d+): .*?(\d+) dollars")
    dollar_distribution = []

    for match in pattern.finditer(response_text):
        # .groups() returns a tuple of all the captured strings
        story_id, dollars = match.groups()
        dollar_distribution.append({
            'story_id': int(story_id),
            'dollars': int(dollars)
        })

    return dollar_distribution

