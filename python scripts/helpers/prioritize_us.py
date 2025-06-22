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

def construct_product_owner_prompt(data):
    stories_formatted = "\n".join(
        [
            f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}"
            for index, story in enumerate(data["stories"])
        ])

    prompt_file_path = os.path.join(os.path.dirname(__file__), "PO_prompt_content.txt")
    with open(prompt_file_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # Insert the req into the template
    prompt_content = prompt_template.format(stories_formatted=stories_formatted)

    print("PO prompt content:", prompt_content)
    return prompt_content


def construct_senior_developer_prompt(data):
    stories_formatted = "\n".join(
        [
            f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}"
            for index, story in enumerate(data["stories"])
        ])

    prompt_file_path = os.path.join(os.path.dirname(__file__), "SD_prompt_content.txt")
    with open(prompt_file_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # Insert the req into the template
    prompt_content = prompt_template.format(stories_formatted=stories_formatted)
    print("SD prompt content:", prompt_content)
    return prompt_content

def construct_senior_qa_prompt(data):
    stories_formatted = "\n".join(
        [
            f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}"
            for index, story in enumerate(data["stories"])
        ])
    
    prompt_file_path = os.path.join(os.path.dirname(__file__), "QA_prompt_content.txt")
    with open(prompt_file_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()
    
    prompt_content = prompt_template.format(stories_formatted=stories_formatted)
    print(stories_formatted)
    print("QA prompt content:", prompt_content)
    return prompt_content

async def agents(stories):
    PO_prompt = construct_product_owner_prompt(
        {"stories": stories}
    )
    SD_prompt = construct_senior_developer_prompt(
        {"stories": stories}
    ) 
    QA_prompt = construct_senior_qa_prompt({"stories": stories})

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
    
    # Step 6: Final Output in table
    await asyncio.sleep(1) 
    # print(prioritization_type, json.dumps(prioritized_stories,indent=4))
    return prioritized_stories

