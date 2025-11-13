import pandas as pd
import numpy as np
import openai
from bertopic.backend import OpenAIBackend
import json


API_KEY = "sk-xxxxxx"
BASE_URL = "https://api.siliconflow.cn/v1"
# EMBEDDING_MODLE = "BAAI/bge-m3"
EMBEDDING_MODLE = "BAAI/bge-large-zh-v1.5"

def get_embedding_model(model_name):
    client = openai.OpenAI(api_key=API_KEY, base_url=BASE_URL)
    embedding_model = OpenAIBackend(client, model_name, batch_size=32)
    return embedding_model

def cosine_distance(a, b):
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    cosine_sim = dot_product / (norm_a * norm_b)
    return cosine_sim

if __name__ == "__main__":
    df = pd.read_excel('../data/merged_issue_forum_release_new.xlsx', sheet_name="Sheet1")
    df = df.fillna('')
    topic_map = {}
    new_source_list = []
    topic_texts = []
    for index, row in df.iterrows():
        if not row["topic"]:
            new_source_list.append({"processed_body": row["processed_body"], "title": row["title"], 'index': index})
            continue
        if row["topic"] not in topic_map:
            topic_map[row["topic"]] = []
            # 与topic title 做相似度关联
            topic_texts.append(row["topic"])
        # 按照title 与 body 进行聚类
        # title = row['title']
        # body = row['processed_body']
        # content = f"- title: {title}\n- body: {body}"
        # content = content[:700]
        # topic_texts.append(content)
        topic_map[row["topic"]].append(index)
    
    print(topic_map)

    embedding_model = get_embedding_model(EMBEDDING_MODLE)
    texts = []
    for item in new_source_list:
        title = item['title']
        body = item['processed_body']
        content = f"- title: {title}\n- body: {body}"
        content = content[:700]
        texts.append(content)

    source_vectors = embedding_model.embed(texts)
    topic_vectors = embedding_model.embed(topic_texts)
    for i, vector in enumerate(source_vectors):
        max_sim = 0
        max_index = -1
        for j, topic_vector in enumerate(topic_vectors):
            sim = cosine_distance(vector, topic_vector)
            if sim > 0.7:
                df.iloc[new_source_list[i]['index']]['topic'] = topic_texts[j]
                print(f"index: {new_source_list[i]['index']}, source: {new_source_list[i]['title']}, topic: {topic_texts[j]}, sim: {sim}")
        # if max_sim > 0.7:
        #     topic = topic_texts[max_index]

    df.to_excel('../data/merged_issue_forum_release_v2.xlsx', index=False, engine='openpyxl')
