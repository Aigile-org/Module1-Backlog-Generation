import sys
import os
import asyncio
import json
from flask import Flask, request, jsonify
from flask_cors import CORS 

# Navigates one directory UP from the current directory
# allows current script to import from the 'helpers' directory.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Now we can import the functions from our custom helper modules
from helpers.generate_us import (generate_user_stories)
from helpers.prioritize_us import agents
from helpers.generate_ac import *
from generate_acceptance_criteria import *

# This is platform-specific code to handle a known issue with asyncio on Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = Flask(__name__)
CORS(app)

# 1. Genrating US
async def refine_text(text):
    prompt = f"Refine the following text by removing meaningless symbols, redundant information, and non-text elements:\n\n{text}"
    return await send_to_llm(
        [
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

@app.route("/generate_and_priortize_us", methods=["POST"])
def generate_us():
    # Flask is a synchronous framework. To run our async code, we need to create
    # and manage an asyncio event loop for each request.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        data = request.get_json()
        req = data["body"]
        print(data["body"])
        # loop.run_until_complete() to execute async functions and wait for their results
        req_refined = loop.run_until_complete(refine_text(req))
        print("req_refined", req_refined)  
        user_stories = loop.run_until_complete(
            generate_user_stories(req=req_refined)
        )
        while True:
            try:
                priortized_us = loop.run_until_complete(
                    agents(user_stories)
                )
                break
            except AttributeError as e:
                print(f"Error parsing response: {e}")
        result = priortized_us
        # 'jsonify' converts the Python dictionary into a proper JSON HTTP response
        # with the correct 'Content-Type' header.
        return jsonify({"result": result})
    except Exception as e:
        # If any error occurs, return a JSON error message with a 500 server error status code
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

@app.route("/generate-single-ac", methods=["POST"])
def generate_single_ac():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ratio = 0.85
    try:
        data = request.get_json()
        userstory = data["body"]
        print(data["body"])
        acceptance_criterias = loop.run_until_complete(GenerateFinalAC(userstory))
        acceptance_criterias = filterSimilarAC(
            AppendingStoriesFromCUU(acceptance_criterias.splitlines()), ratio
        )
        result = acceptance_criterias
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# The code inside this if statement will only
# run when execute this script directly (e.g., 'python api_script.py')
if __name__ == "__main__":
    app.run(port=5000)
