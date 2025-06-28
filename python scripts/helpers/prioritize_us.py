from groq import Groq
import asyncio
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from priortization_helpers import (
    combining_agents,
    construct_prompt,
    send_to_llm
)
def construct_single_agent_prompt(data, agent_type):
    stories_formatted = "\n".join(
        [
            f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}"
            for index, story in enumerate(data["stories"])
        ])

    prompt_file_path = os.path.join(os.path.dirname(__file__), f"{agent_type}_prompt_content.txt")
    with open(prompt_file_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # Insert the req into the template
    prompt_content = prompt_template.format(stories_formatted=stories_formatted)

    print(f"{agent_type} prompt content:", prompt_content)
    return prompt_content

async def agents(stories):
    PO_prompt = construct_single_agent_prompt({"stories": stories},"PO")
    SD_prompt = construct_single_agent_prompt({"stories": stories},"SD") 
    QA_prompt = construct_single_agent_prompt({"stories": stories},"QA")

    # asyncio.gather() takes multiple awaitable objects and runs them all at the same time
    PO_response, SD_response,QA_response = await asyncio.gather(
        send_to_llm(PO_prompt), send_to_llm(SD_prompt), send_to_llm(QA_prompt)
    )
    # Prioritization
    prioritize_prompt = construct_prompt(
        {"stories": stories},
        SD_response,
        QA_response,
        PO_response,
    )
    prioritized_stories = await combining_agents(
        prioritize_prompt, stories
    )
    
    return prioritized_stories

