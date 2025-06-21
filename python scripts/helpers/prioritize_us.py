from groq import Groq
import asyncio
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from priortization_algos import (
    engage_agents_in_prioritization,
    construct_batch_100_dollar_prompt,
    send_to_llm
)


def construct_product_owner_prompt(data, client_feedback=None):
    stories_formatted = "\n".join(
        [
            f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}"
            for index, story in enumerate(data["stories"])
        ]
    )

    prompt_file_path = os.path.join(os.path.dirname(__file__), "PO_prompt_content.txt")
    with open(prompt_file_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # Insert the req into the template
    prompt_content = prompt_template.format(stories_formatted=stories_formatted)

    print("PO prompt content:", prompt_content)
    return prompt_content


def construct_senior_developer_prompt(data, client_feedback=None):
    stories_formatted = "\n".join(
        [
            f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}"
            for index, story in enumerate(data["stories"])
        ]
    )

    prompt_file_path = os.path.join(os.path.dirname(__file__), "SD_prompt_content.txt")
    with open(prompt_file_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # Insert the req into the template
    prompt_content = prompt_template.format(stories_formatted=stories_formatted)
    print("SD prompt content:", prompt_content)
    return prompt_content

def construct_senior_qa_prompt(data, client_feedback=None):
    stories_formatted = "\n".join(
        [
            f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}"
            for index, story in enumerate(data["stories"])
        ]
    )
    prompt_file_path = os.path.join(os.path.dirname(__file__), "QA_prompt_content.txt")
    with open(prompt_file_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()
    prompt_content = prompt_template.format(stories_formatted=stories_formatted)
    print(stories_formatted)
    print("QA prompt content:", prompt_content)
    return prompt_content

async def agents_workflow(
    stories, prioritization_type, client_feedback=None
):
    # Step 1: Greetings
    greetings_prompt = construct_product_owner_prompt(
        {"stories": stories}, client_feedback
    )
    greetings_response = await send_to_llm(greetings_prompt)

    # Step 2: Topic Introduction
    topic_prompt = construct_senior_developer_prompt(
        {"stories": stories}, client_feedback
    )  # logger.info(f"topic_prompt : {topic_prompt}")

    # Step 3: Context and Discussion
    context_prompt = construct_senior_qa_prompt({"stories": stories}, client_feedback)

    # Run Step 2 and Step 3 concurrently
    topic_response, context_response = await asyncio.gather(
        send_to_llm(topic_prompt), send_to_llm(context_prompt)
    )

    # Step 4: Prioritization
    if prioritization_type == "100_DOLLAR":
        # prioritize_prompt = construct_batch_100_dollar_prompt({"stories": stories}, topic_response, context_response)
        prioritize_prompt = construct_batch_100_dollar_prompt(
            {"stories": stories},
            topic_response,
            context_response,
            greetings_response,
        )
        prioritized_stories = await engage_agents_in_prioritization(
            prioritize_prompt, stories
        )
    else:
        raise ValueError(f"Unsupported prioritization type: {prioritization_type}")

    # Step 6: Final Output in table
    await asyncio.sleep(1) 
    # print(prioritization_type, json.dumps(prioritized_stories,indent=4))
    return prioritized_stories

