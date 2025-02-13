import logging
from groq import Groq
import re
logger = logging.getLogger(__name__)

async def send_to_llm(prompt,type_=None):
    # type as too long input makes the mixture model fail -> trying
    client = Groq(
        # api_key="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",
        # api_key="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",
    # api_key="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"
    api_key="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"
    # api_key="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"
    )
    # if type_=="100-dollar":
    model="llama3-8b-8192"
        # model="llama3-70b-8192"
    # else:
        # model="mixtral-8x7b-32768" 
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
    # Access the generated content
    try:
        output = response.choices[0].message.content
        return output
    except AttributeError as e:
        print(f"Error parsing response: {e}")
        return None
#*************100 Dollar**********
def construct_batch_100_dollar_prompt(data, dev_response,qa_response, po_response):
    # Ensure story IDs start from 1
    stories_formatted = '\n'.join([
        f"- Story ID {index + 1}: '{story['user_story']}' {story['epic']} {story['description']}"
        for index, story in enumerate(data['stories'])
    ])

    qa_response_direct = '\n'.join(qa_response)
    dev_response_direct = '\n'.join(dev_response)
    po_response_direct = '\n'.join(po_response)
    # print(stories_formatted)
    # print(qa_response_direct)
    # print(dev_response_direct)
    # print(po_response_direct)

    prompt = (
    "You are the Manager agent, responsible for prioritizing user stories by distributing exactly 100 dollars among them. "
    "Your prioritization is based on inputs from three agents: QA (focused on quality and testing aspects), Developer (focused on technical feasibility), and Product Owner (focused on business and client needs).\n\n"
    "To make a balanced decision, you will:\n"
    "- Aggregate feedback from each agent, averaging their inputs.\n"
    "- Consider the complexity, importance, and alignment with the project’s vision and MVP goals.\n"
    "- Carefully distribute exactly 100 dollars across these stories. **If your allocation does not add up to 100, adjust and recalculate until the total is exactly 100 dollars.**\n\n"
    "**Important Steps for Exact Calculation**:\n"
    "1. Distribute dollars based on importance. Add up your initial allocation.\n"
    "2. If the sum is more than 100, reduce values incrementally across stories until the total is exactly 100.\n"
    "3. If the sum is less than 100, increase values incrementally across stories until the total is exactly 100.\n"
    "4. Repeat these adjustments as needed until the total equals exactly 100.\n\n"
    # f"{feedback_section}"
    "Here are the user stories:\n\n"
    f"{stories_formatted}\n\n"
    "Each role has provided their input based on their expertise:\n\n"
    f"QA's input:\n{qa_response_direct}\n\n"
    f"Developer's context:\n{dev_response_direct}\n\n"
    f"Product Owner's perspective:\n{po_response_direct}\n\n"
    "Please distribute exactly 100 dollars across these stories. Each dollar represents the importance of that story.\n"
    "Your response must strictly follow this format:\n"
    "- Story ID X: Y dollars\n"
    "- Story ID Z: W dollars\n\n"
    "After allocating, **double-check that the total is exactly 100 dollars. If it does not total 100, adjust and verify until it equals exactly 100.**\n\n"
    "provide a summary explanation for the distribution, outlining how the feedback from the three agents, along with complexity and alignment with project goals, influenced the prioritization.\n"
    "The summary should outline how the feedback from the three agents, along with complexity and alignment with project goals, influenced the prioritization."
)
    return prompt

async def engage_agents_in_prioritization(prompt, stories, max_retries=5 ):
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

#*************WSJF************
async def estimate_wsjf(data,  topic_response, context_response):
    
    prioritize_prompt = construct_batch_wsjf_prompt(data, topic_response, context_response)
    #logger.info(f"Prioritize Prompt:\n{prioritize_prompt}")  # Debugging print
    estimated_factors = await send_to_llm(prioritize_prompt)
    # await stream_response_word_by_word(websocket, estimated_factors, "Final Prioritization")
    #logger.info(f"Estimated Factor:\n{estimated_factors}")
    
    wsjf_factors = parse_wsjf_response(estimated_factors)
    logger.info(f"wsjf_factors Factor:\n{wsjf_factors}")
    

    enriched_stories = enrich_original_stories_with_wsjf(data, wsjf_factors)
    logger.info(f"wsjf_factors Factor:\n{enriched_stories}")

    return enriched_stories

def construct_batch_wsjf_prompt(stories, topic_response, context_response):
    stories_formatted = '\n'.join([
        f"- Story ID {story['key']}: '{story['user_story']}' (Epic: '{story['epic']}') - {story['description']}"
        for story in stories
    ])
    
    topic_response_direct = '\n'.join(topic_response)
    context_response_direct = '\n'.join(context_response)
    #print(stories_formatted)
    #print(topic_response_direct)
    #print(context_response_direct)
    
    prompt = (
        "You are a helpful assistant trained in WSJF factor estimation. "
        "For each of the following user stories, please provide estimated numeric values (scale 1 to 10) for the WSJF factors:\n\n"
        f"Here are the stories:\n{stories_formatted}\n\n"
        "Previously, the following points were discussed regarding prioritization:\n"
        f"{topic_response_direct}\n\n"
        "Additionally, here is the context from prior discussions:\n"
        f"{context_response_direct}\n\n"
        "Please consider the following factors and provide values on a scale of 1 to 10, where 1 represents the lowest impact or effort and 10 represents the highest:\n"
        "- Business Value (BV): The relative importance of this story to the business or stakeholders.\n"
        "- Time Criticality (TC): The urgency of delivering this story sooner rather than later.\n"
        "- Risk Reduction/Opportunity Enablement (RR/OE): The extent to which delivering this story can reduce risks or enable new opportunities.\n"
        "- Job Size (JS): The amount of effort required to complete this story, typically measured in story points or ideal days.\n\n"
        "Format the output as:\n"
        "- Story ID X: (Epic: Y)\n"
        "  - Business Value (BV): Z\n"
        "  - Time Criticality (TC): W\n"
        "  - Risk Reduction/Opportunity Enablement (RR/OE): V\n"
        "  - Job Size (JS): U\n\n"
        "For each story, provide a detailed explanation of why it received the allocated values. What is the main reason behind its prioritization? Make sure to include a complete explanation for every story."
    )
    
    return prompt

def parse_wsjf_response(response_text):
    pattern = re.compile(
        r"- Story ID (\d+): \(Epic: .+?\)\n"  # Capture the story ID and the epic
        r"\s+- Business Value \(BV\): (\d+)\n"  # Capture Business Value
        r"\s+- Time Criticality \(TC\): (\d+)\n"  # Capture Time Criticality
        r"\s+- Risk Reduction/Opportunity Enablement \(RR/OE\): (\d+)\n"  # Capture Risk Reduction/Opportunity Enablement
        r"\s+- Job Size \(JS\): (\d+)"  # Capture Job Size
    )

    wsjf_factors = []
    for match in pattern.finditer(response_text):
        story_id, bv, tc, rr_oe, js = match.groups()
        wsjf_factors.append({
            'story_id': int(story_id),
            'wsjf_factors': {
                'BV': int(bv),
                'TC': int(tc),
                'RR/OE': int(rr_oe),
                'JS': int(js)
            }
        })

    return wsjf_factors

# Adding js, oe, tc, bv to original stories
def enrich_original_stories_with_wsjf(original_stories, wsjf_factors):
    wsjf_dict = {factor['story_id']: factor['wsjf_factors'] for factor in wsjf_factors}
    logger.info(f"Original stories:\n{original_stories}")
    logger.info(f"WSJF factors dictionary:\n{wsjf_dict}")

    enriched_stories = []
    for story in original_stories:
        story_id = story['key']
        if story_id in wsjf_dict:
            wsjf_data = wsjf_dict[story_id]
            story['wsjf_factors'] = wsjf_data
            bv = wsjf_data['BV']
            tc = wsjf_data['TC']
            rr_oe = wsjf_data['RR/OE']
            js = wsjf_data['JS']
            wsjf_score = (bv + tc + rr_oe) / js if js != 0 else 0  # Prevent division by zero
            story['wsjf_score'] = wsjf_score
            story['bv'] = bv
            story['tc'] = tc
            story['oe'] = rr_oe
            story['js'] =  js 

            logger.info(f"Story ID {story_id} WSJF factors: {wsjf_data}, WSJF score: {wsjf_score}")
        else:
            story['wsjf_factors'] = {
                'BV': 0,
                'TC': 0,
                'RR/OE': 0,
                'JS': 0
            }
            story['wsjf_score'] = 0
            story['bv'] = 0
            story['tc'] = 0
            logger.warning(f"Story ID {story_id} not found in WSJF factors")

        enriched_stories.append(story)

    enriched_stories = sorted(enriched_stories, key=lambda story: story.get('wsjf_score', 0), reverse=True)
    return enriched_stories


#***********MOSCOW***************
async def estimate_moscow(data,  topic_response, context_response):
    
    prioritize_prompt = construct_batch_moscow_prompt(data, topic_response, context_response)
    estimated_priorities = await send_to_llm(prioritize_prompt)
    # await stream_response_word_by_word(websocket, estimated_priorities, "Final Prioritization")
    
    moscow_priorities = parse_moscow_response(estimated_priorities)
    logger.info(f"MoSCoW Priorities:\n{moscow_priorities}")
    
    enriched_stories = enrich_original_stories_with_moscow(data, moscow_priorities)
    logger.info(f"Enriched Stories with MoSCoW Priorities:\n{enriched_stories}")

    return enriched_stories

def construct_batch_moscow_prompt(stories, topic_response, context_response):
    stories_formatted = '\n'.join([
        f"- Story ID {story['key']}: '{story['user_story']}' (Epic: '{story['epic']}') - {story['description']}"
        for story in stories
    ])

    topic_response_direct = '\n'.join(topic_response)
    context_response_direct = '\n'.join(context_response)

    # print(stories_formatted)
    # print(topic_response_direct)
    # print(context_response_direct)
    
    prompt = (
        "You are a helpful assistant trained in MoSCoW prioritization. "
        "For each of the following user stories, please classify them into one of the following categories based on their importance:\n"
        "- Must Have\n"
        "- Should Have\n"
        "- Could Have\n"
        "- Won't Have\n\n"
        "Here are the stories:\n\n"
        f"{stories_formatted}\n\n"
        "Previously, the following points were discussed regarding prioritization:\n"
        f"{topic_response_direct}\n\n"
        "Additionally, here is the context from prior discussions:\n"
        f"{context_response_direct}\n\n"
        "Format the output as:\n"
        "- Story ID X: Category\n\n"
        "For each story, provide a detailed explanation of why it received the allocated category. What is the main reason behind its prioritization? Make sure to include a complete explanation for every story."
    )
    
    return prompt

# Adding moscow_category to original stories
def enrich_original_stories_with_moscow(original_stories, moscow_priorities):
    moscow_dict = {priority['story_id']: priority['category'] for priority in moscow_priorities}

    enriched_stories = []
    for story in original_stories:
        story_id = story['key']
        story['moscow_category'] = moscow_dict.get(story_id, "No Category")
        enriched_stories.append(story)
        # print("cat",story['moscow_category'])

    enriched_stories.sort(key=lambda x: ['Must Have', 'Should Have', 'Could Have', "Won't Have"].index(x['moscow_category']))
    
    return enriched_stories

def parse_moscow_response(response_text):
    pattern = re.compile(r"- Story ID (\d+): (Must Have|Should Have|Could Have|Won't Have)")
    moscow_priorities = []

    for match in pattern.finditer(response_text):
        story_id, category = match.groups()
        moscow_priorities.append({
            'story_id': int(story_id),
            'category': category
        })

    return moscow_priorities

#*******KANO***********
async def estimate_kano(data, topic_response, context_response):

    prioritize_prompt = construct_batch_kano_prompt(data, topic_response, context_response)
    estimated_priorities = await send_to_llm(prioritize_prompt)
    # await stream_response_word_by_word(websocket, estimated_priorities, "Final Prioritization")
    
    kano_priorities = parse_kano_response(estimated_priorities)
    logger.info(f"KANO Priorities:\n{kano_priorities}")
    
    enriched_stories = enrich_original_stories_with_kano(data, kano_priorities)
    logger.info(f"Enriched Stories with KANO Priorities:\n{enriched_stories}")

    return enriched_stories
def construct_batch_kano_prompt(stories, topic_response, context_response):
    stories_formatted = '\n'.join([
        f"- Story ID {story['key']}: '{story['user_story']}' (Epic: '{story['epic']}') - {story['description']}"
        for story in stories
    ])
    
    topic_response_direct = '\n'.join(topic_response)
    context_response_direct = '\n'.join(context_response)
    
    # print(stories_formatted)
    # print(topic_response_direct)
    # print(context_response_direct)
    
    prompt = (
        "You are a helpful assistant trained in KANO model prioritization. "
        "For each of the following user stories, please classify them into one of the following categories based on their importance:\n"
        "- Basic Needs\n"
        "- Performance Needs\n"
        "- Excitement Needs\n"
        "- Indifferent\n"
        "- Reverse\n\n"
        "Here are the stories:\n\n"
        f"{stories_formatted}\n\n"
        "Previously, the following points were discussed regarding prioritization:\n"
        f"{topic_response_direct}\n\n"
        "Additionally, here is the context from prior discussions:\n"
        f"{context_response_direct}\n\n"
        "Format the output as:\n"
        "- Story ID X: Category\n\n"
        "For each story, provide a detailed explanation of why it received the allocated category. What is the main reason behind its prioritization? Make sure to include a complete explanation for every story."
    )
    
    return prompt

def parse_kano_response(response_text):
    pattern = re.compile(r"- Story ID (\d+): (Basic Needs|Performance Needs|Excitement Needs|Indifferent|Reverse)")
    kano_priorities = []

    for match in pattern.finditer(response_text):
        story_id, category = match.groups()
        kano_priorities.append({
            'story_id': int(story_id),
            'category': category
        })

    return kano_priorities

# Adding kano_category to original stories
def enrich_original_stories_with_kano(original_stories, kano_priorities):
    kano_dict = {priority['story_id']: priority['category'] for priority in kano_priorities}

    enriched_stories = []
    for story in original_stories:
        story_id = story['key']
        story['kano_category'] = kano_dict.get(story_id, "No Category")
        enriched_stories.append(story)

    enriched_stories.sort(key=lambda x: ['Basic Needs', 'Performance Needs', 'Excitement Needs', 'Indifferent', 'Reverse'].index(x['kano_category']))
    
    return enriched_stories

#*********AHP**********8
async def estimate_ahp(data, topic_response, context_response):
    prioritize_prompt = construct_ahp_prompt(data, topic_response, context_response)
    estimated_factors = await send_to_llm(prioritize_prompt)
    # await stream_response_word_by_word(websocket, estimated_factors, "Final Prioritization")
    # print("estimated_factors",estimated_factors)
    prioritized_stories = parse_ahp_stories(estimated_factors)
    # logger.info(f"Prioritized Stories:\n{prioritized_stories}")
    # print("prioritized_stories",prioritized_stories)
    
    enriched_stories = enrich_original_stories_with_ahp(data['stories'], prioritized_stories)
    # logger.info(f"Enriched Stories:\n{enriched_stories}")

    return enriched_stories

def construct_ahp_prompt(data, topic_response, context_response):
    stories_formatted = '\n'.join([
        f"- Story ID {story['key']}: '{story['user_story']}' (Epic: '{story['epic']}') - {story['description']}"
        for story in data['stories']
    ])

    topic_response_direct = '\n'.join(topic_response)
    context_response_direct = '\n'.join(context_response)

    # print(stories_formatted)
    # print(topic_response_direct)
    # print(context_response_direct)
    
    prompt = (
        "You are a helpful assistant. Using the Analytic Hierarchy Process (AHP), prioritize the following user stories based on their relative importance.\n\n"
        f"Here are the stories:\n{stories_formatted}\n\n"
        "Previously, the following points were discussed regarding prioritization:\n"
        f"{topic_response_direct}\n\n"
        "Additionally, here is the context from prior discussions:\n"
        f"{context_response_direct}\n\n"
        "Please provide the following factors for each story on a scale of 1 to 10, where 1 represents the lowest and 10 represents the highest:\n"
        "- Business Value (BV): The importance of this story to the business or stakeholders.\n"
        "- Effort Required (ER): The amount of effort needed to complete this story.\n"
        "- Dependencies (D): The extent to which this story depends on other factors or stories.\n\n"
        "Then calculate the overall weight (W) and overall score (OS) using the following formula:\n"
        "- W = (BV + ER + D) / 3\n"
        "- OS = W\n\n"
        "Return the list of stories in the following format (exactly, e.g: it's very important to include the hashtags, indentation,..):\n\n"
        "### Story ID X: <Story Title>\n"
        "- BV: <value>\n"
        "- ER: <value>\n"
        "- D: <value>\n"
        "- W: <value>\n"
        "- OS: <value>\n\n"
        "For each story, provide a detailed explanation of why it received the allocated values. What is the main reason behind its prioritization? Make sure to include a complete explanation for every story."
    )
    
    return prompt

def parse_ahp_stories(completion_text):
    pattern = re.compile(
        r"### Story ID (\d+):\s*'?(.+?)'?\n"
        r"- BV: (\d+)"
        r".*?\n"  # Skip explanation text
        r"- ER: (\d+)"
        r".*?\n"
        r"- D: (\d+)"
        r".*?\n"
        r"- W: .*?([0-9.]+)"
        r".*?\n"
        r"- OS: ([0-9.]+)",
        re.DOTALL
    )

    prioritized_stories = []
    # print("completion_text",completion_text)
    for match in pattern.finditer(completion_text):
        story_id, story_title, bv, er, d, weight, os = match.groups()
        # print("match",match.groups())
        prioritized_stories.append({
            "ID": int(story_id),
            "user_story": story_title,
            "BV": int(bv),
            "ER": int(er),
            "D": int(d),
            "W": float(weight),
            "OS": float(os),
        })

    # Sort the stories by overall score in descending order
    prioritized_stories.sort(key=lambda x: x["OS"], reverse=True)
    return prioritized_stories

# Adding OS, W, ER, D, BV to original stories
def enrich_original_stories_with_ahp(original_stories, prioritized_stories):
    for story in original_stories:
        story_id = story['key']
        priority_data = next((item for item in prioritized_stories if item["ID"] == story_id), None)
        # print("priority_data",priority_data)
        if priority_data:
            story.update(priority_data)
        else:
            story.update({
                "BV": 0,
                "ER": 0,
                "D": 0,
                "W": 0,
                "OS": 0,
                "priority": float('inf')
            })
            logger.warning(f"Story ID {story_id} not found in prioritized stories")

    enriched_stories = sorted(original_stories, key=lambda x: x.get('OS', 0), reverse=True)
    return enriched_stories
