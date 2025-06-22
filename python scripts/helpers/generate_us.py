import sys
import re
import os

# takes that absolute directory path and adds it to 'sys.path'
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from priortization_helpers import *

def user_story_parser(text_response):
    # Adjusted pattern to match the structured numbered list format
    # r means it's a raw string
    pattern = re.compile(
        r"### User Story \d+:\n"
        #capture everything up to the next newline, non-greedy capture group, to stop at the *first* newline
        r"- User Story: (.*?)\n" 
        r"- Epic: (.*?)\n"
        # to know where the description ends: use lookahead where newline followed by the next story's header
        # OR the absolute end of the entire string (\Z) OR a final newline (\n) as a fallback
        r"- Description: (.*?)(?=\n### User Story \d+:|\Z|\n)",
        # The 're.DOTALL' flag allows the '.' special character in regex to match any character
        # INCLUDING a newline. Without this, the '.*?' for the description would stop
        # at the end of its first line (won't handle multi line descriptions)
        re.DOTALL,
    )

    # returns a list of tuples. Each tuple contains the strings captured by the parentheses ()
    matches = pattern.findall(text_response)
    user_stories = []

    for index, match in enumerate(matches):
        user_stories.append(
            {
                "key": index,
                # .strip() removes any leading/trailing whitespace
                "user_story": match[0].strip(),
                "epic": match[1].strip(),
                "description": match[2].strip(),
            }
        )

    if not user_stories:
        user_stories.append(
            {
                "user_story": "User story not provided",
                "epic": "Epic not provided",
                "description": "Description not provided",
            }
        )

    return user_stories

async def generate_user_stories(req):
    # Read prompt template from file
    prompt_file_path = os.path.join(os.path.dirname(__file__), "generate_us_prompt_content.txt")
    # 'utf-8' is crucial for ensuring that text is read correctly, supporting
    # a wide range of characters and symbols.
    with open(prompt_file_path, "r", encoding="utf-8") as f:
        # read the entire content of the file into a single string
        prompt_template = f.read()

    # Insert the req 
    prompt_content = prompt_template.format(req=req)

    try:
        # 'await' keyword pauses the execution of this function
        generated_content = await send_to_llm(prompt_content)
        parsed_stories = user_story_parser(generated_content)
        return parsed_stories
    except AttributeError as e:
        return None


