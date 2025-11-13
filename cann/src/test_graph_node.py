import pandas as pd
import numpy as np
from bertopic import BERTopic
from transformers.pipelines import pipeline
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from bertopic.representation import KeyBERTInspired, MaximalMarginalRelevance, OpenAI, PartOfSpeech
import jieba
import openai
import requests
from bertopic.backend import OpenAIBackend
from bertopic.backend import BaseEmbedder
from bertopic.vectorizers import ClassTfidfTransformer
import re

API_KEY = "sk-xxxx"
BASE_URL = "https://api.siliconflow.cn/v1"
# EMBEDDING_MODLE = "BAAI/bge-m3"
EMBEDDING_MODLE = "BAAI/bge-large-zh-v1.5"


def get_embedding_model(model_name):
    client = openai.OpenAI(api_key=API_KEY, base_url=BASE_URL)
    embedding_model = OpenAIBackend(client, model_name, batch_size=32)
    return embedding_model


import numpy as np


def cosine_distance(a, b):
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    cosine_sim = dot_product / (norm_a * norm_b)
    return cosine_sim


if __name__ == "__main__":
    df = pd.read_excel('../data/merged_issue_forum_new.xlsx', sheet_name="Sheet1")
    df = df.fillna('')
    texts = []
    tmp_id = {}
    title_texts = []
    for id, row in df.iterrows():
        title = row['title']
        tmp_id[id] = row['title']
        # print(f"id: {id}")
        body = row['processed_body']
        content = f"- title: {title}\n- body: {body}"
        content = content[:700]
        texts.append(content)
        title_texts.append(title)

    embedding_model = get_embedding_model(EMBEDDING_MODLE)
    vectors = embedding_model.embed(texts)
    graph_nodes = []
    tmp_text = [tmp_id[0]]
    # tmp_vector = embedding_model.embed(tmp_text)
    # print(f"tmp_vector: {tmp_vector[0]}")
    # tmp_vector = vectors[0]
    # cosine = cosine_distance(tmp_vector, tmp_vector)
    # print(f"cosine: {cosine}")
    for i, vector in enumerate(vectors):
        # print(f"vector: {vector}")
        # print(f"tmp_id: {tmp_id[i]}")
        for j in range(len(vectors)):
            if i >= j:
                continue
            # tmp_text = [tmp_id[j]]
            tmp_vector = vectors[j]
            cosine = cosine_distance(vector, tmp_vector)
            if cosine > 0.75:
                print(f"id: {i}, title: {tmp_id[i]}, id: {j}, title: {tmp_id[j]}, cosine: {cosine}")
                graph_nodes.append({
                    "in_id": i,
                    "out_id": j,
                    "title_in": tmp_id[i],
                    "title_out": tmp_id[j],
                    "cosine": cosine
                })

    df = pd.DataFrame(graph_nodes)
    df.to_excel('../data/graph_nodes.xlsx', index=False, engine='openpyxl')
