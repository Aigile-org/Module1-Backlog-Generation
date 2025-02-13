from g4f.client import Client
import sys
import asyncio

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# sys.stdout.reconfigure(encoding="utf-8")

# client = Client()
# response = client.chat.completions.create(
#     model="gpt-4",
#     messages=[{"role": "user", "content": "Maximum number of output tokens you can output?"}],
#     web_search=False,
# )
# print(response.choices[0].message.content)


from groq import Groq
import os
client = Groq(
    api_key="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",
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Max number of output size u can generate",
        }
    ],
    model="llama-3.3-70b-versatile",
    stream=False,
)

print(chat_completion.choices[0].message.content)