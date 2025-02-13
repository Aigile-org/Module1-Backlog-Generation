from groq import Groq
import asyncio
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from priortization_algos import (
    estimate_ahp,
    estimate_kano,
    estimate_moscow,
    estimate_wsjf,
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

    # feedback_section = ""
    # if client_feedback:
    #     feedback_section = "As you prioritize, consider the following feedback provided by the client:\n\n" + '\n'.join(['- ' + fb for fb in client_feedback]) + "\n\n"

    # print("Formatted Stories:")
    # print(stories_formatted)
    prompt = (
        "You are an experienced Product Owner who has successfully delivered several products from concept to market. "
        # f"{feedback_section}"
        "Distribute 100 dollars (points) among the following user stories. Each dollar represents the relative importance of that story. "
        "Please distribute exactly 100 dollars across these stories, making sure the total equals exactly 100 dollars. Each dollar represents the importance of that story.\n"
        "Ensure the total adds up to 100 dollars. Use this format:\n"
        "- ID X: Y dollars\n"
        "- ID Z: W dollars\n\n"
        "Here are the stories:\n\n"
        f"{stories_formatted}\n\n"
        "After allocating, double-check that the total is exactly 100 dollars. If it does not total 100, adjust and verify until it equals exactly 100.\n"
        "Provide a brief summary of two or three lines, explaining your prioritization approach, focusing on maximizing customer value and aligning with strategic goals."
    )
    return prompt


def construct_senior_developer_prompt(data, client_feedback=None):
    stories_formatted = "\n".join(
        [
            f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}"
            for index, story in enumerate(data["stories"])
        ]
    )

    # feedback_section = ""
    # if client_feedback:
    #     feedback_section = "As you prioritize, take into account the following feedback from the client:\n\n" + '\n'.join(['- ' + fb for fb in client_feedback]) + "\n\n"
    prompt = (
        "You are a Senior Developer with several years of programming experience. "
        # f"{feedback_section}"
        "Distribute 100 dollars (points) among the following user stories. Each dollar represents the relative importance of that story. "
        "Please distribute exactly 100 dollars across these stories, making sure the total equals exactly 100 dollars. Each dollar represents the importance of that story.\n"
        "Ensure the total adds up to 100 dollars. Use this format:\n"
        "- ID X: Y dollars\n"
        "- ID Z: W dollars\n\n"
        "Here are the stories:\n\n"
        f"{stories_formatted}\n\n"
        "After allocating, double-check that the total is exactly 100 dollars. If it does not total 100, adjust and verify until it equals exactly 100.\n"
        "Provide a brief summary of two or three lines,, focusing on technical dependencies, efficient project flow, and best practices."
    )
    return prompt


def construct_senior_qa_prompt(data, client_feedback=None):
    stories_formatted = "\n".join(
        [
            f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}"
            for index, story in enumerate(data["stories"])
        ]
    )

    # feedback_section = ""
    # if client_feedback:
    #     feedback_section = "As you prioritize, consider the following feedback from the client:\n\n" + '\n'.join(['- ' + fb for fb in client_feedback]) + "\n\n"

    prompt = (
        "You are a Senior QA professional focused on quality and reliability. "
        # f"{feedback_section}"
        "Distribute 100 dollars (points) among the following user stories. Each dollar represents the relative importance of that story. "
        "Ensure the total adds up to 100 dollars. Use this format:\n"
        "Please distribute exactly 100 dollars across these stories, making sure the total equals exactly 100 dollars. Each dollar represents the importance of that story.\n"
        "- ID X: Y dollars\n"
        "- ID Z: W dollars\n\n"
        "Here are the stories:\n\n"
        f"{stories_formatted}\n\n"
        "After allocating, double-check that the total is exactly 100 dollars. If it does not total 100, adjust and verify until it equals exactly 100.\n"
        "Provide a brief summary of two or three lines, emphasizing risk mitigation, quality, and client satisfaction."
    )
    return prompt

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
        # print("Final 100 dollar", prioritized_stories)
        # Order by wsjf_score = (bv + tc + rr_oe) / js if js != 0 else 0  # Prevent division by zero 
    elif prioritization_type == "WSJF":
        prioritized_stories = await estimate_wsjf(
            stories, topic_response, context_response
        )
        # Sort by ['Must Have', 'Should Have', 'Could Have', "Won't Have"], 0: highest priority
    elif prioritization_type == "MOSCOW":
        prioritized_stories = await estimate_moscow(
            stories, topic_response, context_response
        )
        # Sort by ['Basic Needs', 'Performance Needs', 'Excitement Needs', 'Indifferent', 'Reverse'], 0: highest priority
    elif prioritization_type == "KANO":
        prioritized_stories = await estimate_kano(
            stories,  topic_response, context_response
        )
        # Sort by OS where W = (BV + ER + D) / 3, OS = W
    elif prioritization_type == "AHP":
        prioritized_stories = await estimate_ahp(
            {"stories": stories}, topic_response, context_response
        )
    else:
        raise ValueError(f"Unsupported prioritization type: {prioritization_type}")

    # Step 6: Final Output in table
    await asyncio.sleep(1) 
    # print(prioritization_type, json.dumps(prioritized_stories,indent=4))
    return prioritized_stories

