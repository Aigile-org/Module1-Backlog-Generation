import logging
from groq import Groq, RateLimitError
import os
import re

# creates a logger instance that is specific to this file
logger = logging.getLogger(__name__)

api_key = "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"

async def send_to_llm(prompt):
    # llama3: This is the model family, Llama 3 from Meta AI
    # 70b: This refers to the number of parameters—70 billion parameters, which is a measure of the model's size and complexity.
    # 131,072: context window size, meaning the model can consider up to 131,072 "tokens"
    # context window size: total, combined limit for both the past context (input) and the future generation (output) added together. 
    # The more space input takes, the less space is left for the output
    model = "llama-3.3-70b-versatile"
    
    try:
        print(f"Attempting API call with primary key...")
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
        print(f"Success with primary key")
        output = response.choices[0].message.content
        return output
        
    except RateLimitError as e:
        # This block catches the specific rate limit error
        # e.body' often contains a JSON object with details
        print(f"Rate limit reached for key. Error details: {e.body.get('error', {}).get('message')}")
        
    except Exception as e:
        # Catch other potential exceptions (e.g., authentication, connection errors)
        print(f"An unexpected error occurred: {e}")
                
    print("Could not get a response from the API.")
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

