import sys
import asyncio
import re
# from groq import Groq
import os
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from priortization_algos import *
def parse_user_stories(text_response):
    # Adjusted pattern to match the structured numbered list format, including the last line without a newline
    pattern = re.compile(
        r"### User Story \d+:\n"
        r"- User Story: (.*?)\n"
        r"- Epic: (.*?)\n"
        r"- Description: (.*?)(?=\n### User Story \d+:|\Z|\n)",
        re.DOTALL
    )

    matches = pattern.findall(text_response)
    user_stories = []

    for index,match in enumerate(matches):
        user_stories.append({
            'key':index,
            "user_story": match[0].strip(),
            "epic": match[1].strip(),
            "description": match[2].strip(),
        })

    if not user_stories:
        user_stories.append({
            "user_story": "User story not provided",
            "epic": "Epic not provided",
            "description": "Description not provided",
        })

    # return json.dumps(user_stories, indent=4)
    return user_stories

async def generate_user_stories_with_epics( req):

    prompt_content = (
    "You are a helpful assistant tasked with generating unique user stories and grouping them under relevant epics based on any project vision or MVP goal provided.\n"
    "When generating user stories, ensure they are grouped under relevant epics based on overarching themes, functionalities, or MVP goals identified. Each epic should contain multiple user stories that cover various aspects of the same theme or functionality. "
    "Aim to generate as many stories as necessary to fully cover the scope of the project, with **no upper limit on the number of user stories**. Focus on breaking down large functionalities into individual, task-specific stories.\n\n"
    "Given the project requirements: '{req}', generate a comprehensive and distinct set of user stories that align with these core elements. "
    "Ensure each story comprehensively addresses both functional and technical aspects relevant to the project, with a focus on supporting the project's primary vision and achieving a highly detailed MVP.\n\n"
    "For each user story, provide the following details:\n"
    "1. User Story: A clear and concise description that encapsulates a specific need or problem. Example: 'As a <role>, I want to <action>, in order to <benefit>'. Each story should directly support the project's vision or contribute towards a functional MVP.\n"
    "2. Epic: The broad epic under which the user story falls. Each epic can encompass multiple related user stories that share a similar scope or functionality.\n"
    "3. Description: Detailed acceptance criteria for the user story, specifying what success looks like for the story to be considered complete, particularly in terms of MVP completion and alignment with the vision.\n\n"
    "Additional Guidance:\n"
    "- **Encourage atomic functionalities**: Create user stories for individual actions and small steps within each phase of the MVP.\n"
    "- **Ensure maximum detail**: Generate highly specific user stories that focus on even the smallest functionalities, such as scanning, logging in, generating reports, and handling errors.\n"
    "- **No upper limit**: Keep breaking down actions until all core and sub-tasks within the MVP are covered.\n\n"
    "Please use the following format for each story:\n"
    "### User Story X:\n"
    "- User Story: As a <role>, I want to <action>, in order to <benefit>.\n"
    "- Epic: <epic> (This epic may encompass multiple related user stories)\n"
    "- Description: Detailed and clear acceptance criteria that define the success of the user story, particularly in achieving MVP functionality and supporting the overall vision.\n"
).format(req=req)
    
#     client = Groq(
#         api_key="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",
#     )
#     response = client.chat.completions.create(
#     messages=[
#         {
#             "role": "user",
#             "content":prompt_content,
#         }
#     ],
#     model="llama3-70b-8192",
#     stream=False,
# )
    
    # Access the generated content
    try:
        generated_content = await send_to_llm(prompt_content)
        # print(generated_content)
        parsed_stories = parse_user_stories(generated_content)
        # print(json.dumps(parsed_stories,indent=4))
        return parsed_stories
    except AttributeError as e:
        # print(f"Error parsing response: {e}")
        return None
    # if response.status_code == 200:
    #     response_data = response.json()
    #     generated_content = response.choices[0].message.content
    #     print(generated_content)
    #     parsed_stories = parse_user_stories(generated_content)
    #     print(parsed_stories)
    #     return parsed_stories
    # else:
    #     raise Exception("Failed to process the request with OpenAI: " + response.text)
    
def generate_check_stories_prompt(stories, framework):
    stories_formatted = ''
    
    for index, story in enumerate(stories):
        if not isinstance(story, dict):
            print(f"Error: Story at index {index} is not a dictionary: {story}")
            continue
        
        # Ensure 'status' key is handled properly
        stories_formatted += (
            # f"- Story ID {index}: "
            f"'{story['user_story']}' "
            f"{story['epic']} "
            f"{story['description']} "
            f"{story.get('status', '')}\n"
        )

    return (
        "You are a meticulous assistant capable of evaluating user stories based on established frameworks.\n"
        f"Given the following list of user stories, evaluate each one to ensure it adheres to the principles of the {framework} framework.\n"
        "For each user story, provide the following details:\n"
        "1. User Story: The original user story.\n"
        "2. Framework: The framework used for evaluation ({framework}).\n"
        "3. Compliance: Whether the user story complies with the framework.\n"
        "4. Issues: If not compliant, list the specific issues.\n\n"
        "5. Description: The original description.\n"
        "6. Status: The original status.\n"
        "7. Epic: The original epic.\n"
        "Please use the following format for each evaluation:\n"
        "### User Story X:\n"
        "- User Story: <original_user_story>\n"
        "- Framework: {framework}\n"
        "- Compliance: <yes/no>\n"
        "- Issues: <list_of_issues>\n\n"
        "- Description: <original_description>\n"
        "- Status: <original_status>\n"
        "- Epic: <original_epic>\n"
        f"{stories_formatted}"
    )
def parse_checked_stories(completion_text):
    pattern = re.compile(
        r"### User Story \d+:\n"
        r"- User Story: (.*?)\n"
        r"- Framework: (.*?)\n"
        r"- Compliance: (.*?)\n"
        r"- Issues: (.*?)\n"
        r"- Description: (.*?)\n"
        r"- Status: (.*?)\n"
        # r"- Epic: (.*?)(?=\n### User Story \d+|\Z|\n)",
        r"- Epic: (.*?)\n",
        re.DOTALL
    )

    matches = pattern.findall(completion_text)
    checked_stories = []

    for match in matches:
        checked_stories.append({
            "user_story": match[0].strip(),
            "framework": match[1].strip(),
            "compliance": match[2].strip().lower() == 'yes',
            "issues": match[3].strip(),
            "description": match[4].strip(),
            "status": match[5].strip(),
            "epic": match[6].strip(),
        })

    return checked_stories
async def check_stories_with_framework(stories, framework):
    prompt = generate_check_stories_prompt(stories, framework)

#     client = Groq(
#         api_key="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",
#     )
#     response = client.chat.completions.create(
#     messages=[
#         {
#             "role": "user",
#             "content":prompt,
#         }
#     ],
#     model="llama3-70b-8192",
#     stream=False,
# )
    # Access the generated content
    try:
        completion_text = await send_to_llm(prompt)
        # print(generated_content)
        checked_stories = parse_checked_stories(completion_text)
        # print(json.dumps(checked_stories,indent=4))
        return checked_stories
    except AttributeError as e:
        print(f"Error parsing response: {e}")
        return None