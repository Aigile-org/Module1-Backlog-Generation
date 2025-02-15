import sys
import os
import asyncio
import json

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers.generate_us import (
    generate_user_stories_with_epics,
    check_stories_with_framework,
)
from helpers.prioritize_us import agents_workflow
from helpers.generate_ac import *
from generate_acceptance_criteria import *
from g4f.client import Client

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# objective='The goal of the Tampere City RAG (Retrieve and Generate) Application is to create an AI-driven chatbot that answers visitor questions about the Land Use and Construction Act. The chatbot will function in Finnish, both for input questions and output answers. An English version will be considered later. Data Sources The information will be sourced from the following websites, all in Finnish: 1) Link 1: Finnish legislation website containing the Land Use and Construction Act. 2) Link 2: City planning and zoning information for Tampere. 3) Link 3: Information on building permits, and information services in Tampere. Additionally, a relevant FAQ has been provided from the customer for understanding: • https://www.kouvola.fi/asuminen-ja-ymparisto/rakentaminen/rakennusvalvonta/useinkysyttya-pienet-pihalla-tehtavat-tyot-ja-rakennusprojektit/ Technical Approach ▪ Web Scraping: Extract data from the three specified websites. ▪ Translation: Translate the extracted data into English for internal processing (initially, focus on Finnish for the MVP). ▪ Data Structuring: Convert the data into a structured format suitable for use with a Large Language Model (LLM). ▪ Storage: Use a vector database like Pinecone or Qdrant to store the structured data. ▪ LLM Integration: Utilize the structured data to enable the LLM to generate accurate and relevant responses. ▪ Final Deployment: Deploy the AI chatbot on the official Tampere City website (e.g., Tampere.fi). Not now. Example User Questions • Voinko kaataa puun tontiltani?" (Can I cut down a tree from my plot?) • "Entä pensasaita? Tarvitseeko luvan?" (What about a hedge? Need a permit?)'
vision = "Aligning more than 500 different vendors and API solutions is difficult. The current system struggles to manage 500 suppliers, each with different vendors, making it difficult to centralize and compare prices. The complexity of tracking menu costs, resource costs, price changes, and different vendors creates significant challenges. A unified platform is needed to streamline this process, allowing for the extraction and analysis of data from various vendor PDFs. This platform would store the data in a vector format to provide better insights. Nick will provide more PDFs of different vendors to run the experiment smoothly. The current system struggles to manage 500 suppliers, each with different vendors, making it difficult to centralize and compare prices."
mvp = "The MVP aims to develop a chatbot capable of real-time analysis, providing insights into supplier offerings. The final LLM (Large Language Model) assistant will help managers make informed decisions based on cost analysis, ensuring profitable deals. The first phase targets a release date of July 23rd. Technical Approach PDF Extraction: Obtain PDFs from different vendors of each supplier and extract the content. Translation: Translate the extracted data into English for internal processing. Data Structuring: Convert the data into a structured format suitable for use with a Large Language Model (LLM). Storage: Store the structured data in a vector database like MongoDB. LLM Integration: Utilize the structured data to enable the LLM to generate accurate and relevant responses through well-crafted prompts or queries. Demo: Aim to deliver a functional demo by the third week of July. Use Cases or Query Prompts Ingredient Requirement for Lasagna: Determine the required ingredients and their quantities for making 10 dishes of lasagna, along with the current rates. Supplier Rate Comparison for Pasta: Identify which supplier offers the best rates and deals for making pasta this month. Recipe and Cost Analysis for Lasagna: Retrieve the recipe for lasagna, list all necessary ingredients, and calculate the cost of preparing 20 plates for the next day. Future Prospects API Development: Provide APIs for the team to upload PDFs and perform detailed insights on historical data and various offers. Enhanced Data Analysis: Enable deeper analysis of historical data and trends to optimize procurement and cost management. This approach ensures a streamlined process for managing supplier data, facilitating better decision-making through advanced data analysis and LLM integration."


# 1. Genrating US
async def refine_text(text):
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # sys.stdout.reconfigure(encoding="utf-8")
    prompt = f"Refine the following text by removing meaningless symbols, redundant information, and non-text elements:\n\n{text}"
    return await send_to_llm(
        [
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )
    # print(response.choices[0].message.content)


# Main async function so we needn't use asyncio.run with calling each async function
async def pipeline(req):
    # req=vision+mvp
    req_refined = await refine_text(req)
    # print(req_refined)
    # print(req_refined)
    ratio = 0.95
    # 1. Generate User Stories
    user_stories = await generate_user_stories_with_epics(req=req_refined)
    # print(user_stories)
    # Define the output file path
    # output_file = "user_stories_llama3_8b_8192.py"
    # Write user stories as a Python dictionary to a file
    # with open(output_file, "w") as file:
    #     file.write("user_stories = ")
    #     file.write(repr(user_stories))

    # 2. Check Against Framework
    # await check_stories_with_framework(user_stories, "INVEST")

    # 3. Prioritize User Stories
    while True:
        try:
            priortized_us = await agents_workflow(user_stories, "AHP")
            break
        except AttributeError as e:
            print(f"Error parsing response: {e}")
    # print(priortized_us)
    # 4. Generate Acceptance Criteria
    for us in priortized_us:
        # print(us)  # Optional: Debugging output
        acceptance_criterias = await GenerateFinalAC(us["user_story"])
        us["ac"] = filterSimilarAC(
            AppendingStoriesFromCUU(acceptance_criterias.splitlines()), ratio
        )

    # 5. Print the final prioritized user stories with ACs
    print(json.dumps(priortized_us, indent=4), flush=True)
    return priortized_us


# input = sys.argv[1]
# output = asyncio.run(pipeline(input))
# print(output)
# sys.stdout.flush()

from flask import Flask, request, jsonify
from flask_cors import CORS  # Add this

app = Flask(__name__)
CORS(app)


@app.route("/generate-us", methods=["POST"])
def generate_us():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        data = request.get_json()
        req = data["body"]
        print(data["body"])
        req_refined = loop.run_until_complete(refine_text(req))
        print("req_refined", req_refined)  # 1. Generate User Stories
        user_stories = loop.run_until_complete(
            generate_user_stories_with_epics(req=req_refined)
        )
        result = user_stories
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/priortize-us", methods=["POST"])
def priortize_us():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        data = request.get_json()
        user_stories = data["body"]
        print(data["body"])
        while True:
            try:
                priortized_us = loop.run_until_complete(
                    agents_workflow(user_stories, "AHP")
                )
                break
            except AttributeError as e:
                print(f"Error parsing response: {e}")
        result = priortized_us
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/generate-ac", methods=["POST"])
def generate_ac():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ratio = 0.85
    try:
        data = request.get_json()
        priortized_us = data["body"]
        print(data["body"])
        for us in priortized_us:
            # print(us)  # Optional: Debugging output
            acceptance_criterias = loop.run_until_complete(
                GenerateFinalAC(us["user_story"])
            )
            us["ac"] = filterSimilarAC(
                AppendingStoriesFromCUU(acceptance_criterias.splitlines()), ratio
            )
        result = priortized_us
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000)
