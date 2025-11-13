import pandas as pd
import numpy as np
import openai
from bertopic.backend import OpenAIBackend

API_KEY = "sk-xxxxxx"
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
    df = pd.read_excel('../data/merged_issue_forum_release_v2.xlsx', sheet_name="Sheet1")
    df = df.fillna('')
    texts = []
    id2index_map = []
    title_texts = []
    for id, row in df.iterrows():
        if row["topic"]:
            continue
        title = row['title']
        # print(f"id: {id}")
        body = row['processed_body']
        content = f"- title: {title}\n- body: {body}"
        content = content[:700]
        texts.append(content)
        id2index_map.append({"id": id, "title": title})
        title_texts.append(title)

    embedding_model = get_embedding_model(EMBEDDING_MODLE)
    vectors = embedding_model.embed(texts)
    graph_nodes = []
    # print(f"tmp_vector: {tmp_vector[0]}")
    # tmp_vector = vectors[0]
    # cosine = cosine_distance(tmp_vector, tmp_vector)
    # print(f"cosine: {cosine}")
    for i, vector in enumerate(vectors):
        # print(f"vector: {vector}")
        for j in range(len(vectors)):
            if i >= j:
                continue
            tmp_vector = vectors[j]
            cosine = cosine_distance(vector, tmp_vector)
            if cosine > 0.75:
                in_id = id2index_map[i].get("id")
                in_title = id2index_map[i].get("title")
                out_id = id2index_map[j].get("id")
                out_title = id2index_map[j].get("title")
                print(f"id: {in_id}, title: {in_title}, id: {out_id}, title: {out_title}, cosine: {cosine}")
                graph_nodes.append({
                    "in_id": in_id,
                    "out_id": out_id,
                    "title_in": in_title,
                    "title_out": out_title,
                    "cosine": cosine
                })
    
    df = pd.DataFrame(graph_nodes)
    df.to_excel('../data/graph_nodes.xlsx', index=False, engine='openpyxl')
