import sys
import asyncio
import re
import os
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from priortization_algos import *

def user_story_parser(text_response):
    # Adjusted pattern to match the structured numbered list format, including the last line without a newline
    pattern = re.compile(
        r"### User Story \d+:\n"
        r"- User Story: (.*?)\n"
        r"- Epic: (.*?)\n"
        r"- Description: (.*?)(?=\n### User Story \d+:|\Z|\n)",
        re.DOTALL,
    )

    matches = pattern.findall(text_response)
    user_stories = []

    for index, match in enumerate(matches):
        user_stories.append(
            {
                "key": index,
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
    with open(prompt_file_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # Insert the req into the template
    prompt_content = prompt_template.format(req=req)

    try:
        generated_content = await send_to_llm(prompt_content)
        parsed_stories = user_story_parser(generated_content)
        return parsed_stories
    except AttributeError as e:
        return None


