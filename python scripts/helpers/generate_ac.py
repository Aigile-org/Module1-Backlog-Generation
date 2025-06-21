# from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq

API_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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"
]

async def send_to_llm(prompt, type_=None):
    """
    Sends a prompt to the Groq LLM API, handling rate limits by cycling through a list of API keys.
    """
    model = "llama3-70b-8192"

    # Iterate through the list of available API keys
    for i, api_key in enumerate(API_KEYS):
        try:
            print(f"Attempting API call with key #{i + 1}...")
            client = Groq(api_key=api_key)

            response = client.chat.completions.create(
                messages=prompt,
                model=model,
                stream=False,
            )

            # If the request is successful, return the output
            print(f"Success with key #{i + 1}.")
            output = response.choices[0].message.content
            return output

        except RateLimitError as e:
            # This block catches the specific rate limit error
            print(
                f"Rate limit reached for key #{i + 1}. Error details: {e.body.get('error', {}).get('message')}"
            )
            if i < len(API_KEYS) - 1:
                print("Switching to the next API key.")
            else:
                print("All API keys have been rate-limited.")
            # The loop will continue to the next key

        except Exception as e:
            # Catch other potential exceptions (e.g., authentication, connection errors)
            print(f"An unexpected error occurred with key #{i + 1}: {e}")
            if i < len(API_KEYS) - 1:
                print("Trying next key...")
            else:
                print("All keys failed.")

    # If the loop completes without a successful call, return None
    print("Could not get a response from the API. All keys are likely exhausted.")
    return None


def readFewshotExamples(path, id):

    usFile = open(path + "Examples/example_" + id + "_US.txt", "r", encoding="utf8")
    us = usFile.read()

    exampleRA = open(path + "Examples/example_" + id + "_RA.txt", "r", encoding="utf8")
    ra = exampleRA.read()

    exampleQA = open(path + "Examples/example_" + id + "_QA.txt", "r", encoding="utf8")
    qa = exampleQA.read()

    exampleOthers = open(
        path + "Examples/example_" + id + "_Others.txt", "r", encoding="utf8"
    )
    others = exampleOthers.read()

    return us, ra, qa, others


def readInstructionFile(filename):
    f = open(filename, "r")
    content = f.read()
    return content


def constructeInputPromptForACGeneration(us):
    path = "/home/mou3/mysite/python scripts/"
    usFile, raExample, qaExample, othersExample = readFewshotExamples(path, "1")
    usFile2, raExample2, qaExample2, othersExample2 = readFewshotExamples(path, "2")
    usFile3, raExample3, qaExample3, othersExample3 = readFewshotExamples(path, "3")
    initialContent = readInstructionFile(path + "Instructions/initialSystem.txt")
    roleInstructions = readInstructionFile(path + "Instructions/Roles.txt")
    outputFormat = readInstructionFile(path + "Instructions/outputFormat.txt")

    contextAndRole = [
        {
            "role": "system",
            "content": initialContent
            + "\n"
            + outputFormat
            + "\n"
            + "Here are role instructions in this activity.\n"
            + roleInstructions
            + "\n",
        }
    ]

    command_1 = "Write acceptance criteria for the given user story as the Product Owner and Business Analyst:\n"
    command_2 = "Update or supplement the above acceptance criteria for given user story as a Quality Analyst if necessary.\n"
    command_3 = "Update or supplement the above acceptance criteria for given user story as other team members if necessary.\n"

    learning = [
        {"role": "user", "content": command_1 + usFile + "\n"},
        {"role": "assistant", "content": raExample + "\n"},
        {"role": "user", "content": command_2 + usFile + " \n"},
        {"role": "assistant", "content": qaExample + "\n"},
        {"role": "user", "content": command_3 + usFile + " \n"},
        {"role": "assistant", "content": othersExample + "\n"},
        {"role": "user", "content": command_1 + usFile2 + "\n"},
        {"role": "assistant", "content": raExample2 + "\n"},
        {"role": "user", "content": command_2 + usFile2 + " \n"},
        {"role": "assistant", "content": qaExample2 + "\n"},
        {"role": "user", "content": command_3 + usFile2 + " \n"},
        {"role": "assistant", "content": othersExample2 + "\n"},
        {"role": "user", "content": command_1 + usFile3 + "\n"},
        {"role": "assistant", "content": raExample3 + "\n"},
        {"role": "user", "content": command_2 + usFile3 + " \n"},
        {"role": "assistant", "content": qaExample3 + "\n"},
        {"role": "user", "content": command_3 + usFile3 + " \n"},
        {"role": "assistant", "content": othersExample3 + "\n"},
    ]

    prompts = contextAndRole + learning

    completionComands = [
        {"role": "user", "content": command_1 + "\n" + us + "\n"},
        {"role": "user", "content": command_2 + "\n" + us + "\n"},
        {"role": "user", "content": command_3 + "\n" + us + "\n"},
    ]

    myInput = [prompts, completionComands]

    return myInput


def FilteringEmptyLines(string_prompt):
    lines = string_prompt.split("\n")
    filtered_string = ""
    not_empty_lines = [line for line in lines if line.strip() != ""]
    for line in not_empty_lines:
        filtered_string += line + "\n"
    return filtered_string


# CUU for create update update
async def GenerateACByCUU(us, promptInput):
    # history = []
    # outputs = []
    output = ""
    stage = "C"  # C for create acceptance criteria, U for update acceptance criteria
    # allCompletions = []

    initialPrompt = promptInput[0]
    input = promptInput[1]
    preOutput = ""

    ## Pop user and assistant prompt for each iteration, with system role in first iteration
    while input:
        if stage == "C":
            newInput = input.pop(0)
            currentInput = initialPrompt + [newInput]  # system, user, assistant

            currentOutput = await send_to_llm(currentInput)
            currentOutput = FilteringEmptyLines(currentOutput)
            preOutput = currentOutput
            stage = "U"

            output = output + currentOutput + "\n"
            continue

        else:
            newInput = input.pop(0)
            updatedInput = preOutput + newInput["content"]
            newInput["content"] = updatedInput
            currentInput = initialPrompt + [newInput]  # system, user, assistant
            currentOuput = await send_to_llm(currentInput)
            currentOuput = FilteringEmptyLines(currentOuput)
            preOutput = currentOutput

            output = output + currentOuput + "\n"
            continue

    return output


# Appending stories from each of create, update, update
def AppendingStoriesFromCUU(acceptance_criterias):
    all_output = []
    is_start = False
    for i in acceptance_criterias:
        # i = i.strip()
        if i == "<start>":
            is_start = True
            continue
        elif i == "<end>":
            is_start = False
            continue
        elif is_start:
            # Extract the text after the number and the dot
            all_output.append(i[(i.find(".") + 2) :])
            continue
        else:
            continue
    return all_output


def checkSimilarity(sen1, sen2):
    # Encode the sentences into embeddings
    # vectorizer = TfidfVectorizer()
    embeddings = vectorizer.fit_transform([sen1, sen2])  # Must be a list of sentences

    # Convert to dense format for similarity calculation
    emb1, emb2 = embeddings.toarray()

    # Compute cosine similarity
    score = cosine_similarity([emb1], [emb2])[0][0]

    return score


# Load the pre-trained sentence transformer model (BERT-based)
# model = SentenceTransformer('all-MiniLM-L6-v2')
vectorizer = TfidfVectorizer()


def filterSimilarAC(ac, ratio):
    finalAC = []
    for i in ac:
        if len(finalAC) == 0:
            finalAC.append(i)
        else:
            appendFlag = True
            for j in finalAC:
                score = checkSimilarity(i, j)
                if score > ratio:
                    appendFlag = False
                    break
            if appendFlag:
                finalAC.append(i)

    return finalAC
