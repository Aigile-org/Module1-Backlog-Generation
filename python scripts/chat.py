# from g4f.client import Client
# import sys
# import asyncio


# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# sys.stdout.reconfigure(encoding="utf-8")

# client = Client()
# response = client.embeddings.create(  model="text-embedding-ada-002",
#         input="hello")
# print(response["data"][0]["embedding"])



# from groq import Groq
# import os
# client = Groq(
#     api_key="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",
# )

# chat_completion = client.chat.completions.create(
#     messages=[
#         {
#             "role": "user",
#             "content": "Max number of output size u can generate",
#         }
#     ],
#     model="llama-3.3-70b-versatile",
#     stream=False,
# )

# print(chat_completion.choices[0].message.content)

# import fasttext.util
# fasttext.util.reduce_model(fasttext.load_model('cc.en.300.bin'), 100) 
# # Get word vector
# word_vector = ft.get_word_vector("hello")
# print(word_vector)

# from sklearn.feature_extraction.text import TfidfVectorizer

# vectorizer = TfidfVectorizer()
# sentences = ["Hello, how are you?", "I am doing great!"]
# X = vectorizer.fit_transform(sentences)

# # print(X.toarray())  # Convert sparse matrix to array
# import gensim.downloader as api

# # Load pre-trained Word2Vec embeddings (this downloads ~1.5GB)
# word2vec = api.load("glove-wiki-gigaword-50")

# import numpy as np
# import nltk
# from nltk.tokenize import word_tokenize

# nltk.download('punkt')  # Ensure NLTK tokenizer is available

# def sentence_embedding(sentence, model):
#     words = word_tokenize(sentence.lower())  # Tokenize and lowercase
#     vectors = [model[word] for word in words if word in model]  # Get word vectors
#     return np.mean(vectors, axis=0) if vectors else np.zeros(300)  # Average word vectors






from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
vectorizer = TfidfVectorizer()
def checkSimilarity(sen1, sen2):
    embeddings = vectorizer.fit_transform([sen1, sen2])

    # Convert sparse matrix to dense arrays
    emb1, emb2 = embeddings.toarray()

    # Compute cosine similarity
    score = cosine_similarity([emb1], [emb2])[0][0]
    print(score)

    return score
checkSimilarity("The chatbot interface should have a user-friendly design that allows users to easily interact with it through text or voice inputs.","The chatbot should be able to understand and respond to user queries in real-time, providing accurate and relevant information.")