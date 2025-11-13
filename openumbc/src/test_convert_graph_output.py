import pandas as pd
import numpy as np
import pandas as pd
import openai
from bertopic.backend import OpenAIBackend
import numpy as np
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
    topic_info = pd.read_excel('../data/topic_graph_info_merged.xlsx', sheet_name="Sheet1")
    topic_doc = pd.read_excel('../data/topic_graph_doc.xlsx', sheet_name="Sheet1")
    origin_data = pd.read_excel('../data/merged_issue_forum_release_v2.xlsx', sheet_name="Sheet1")
    topics = {}

    for topic_index, row in topic_info.iterrows():
        summary = str(row['summary'])
        # topic = str(row['Topic'])
        topic = str(topic_index)
        topic_node = eval(str(row['topic node']))
        texts = []
        for node in topic_node:
            title = topic_doc.loc[node]["title"]
            body = topic_doc.loc[node]["processed_body"]
            content = f"- title: {title}\n- body: {body}"
            texts.append(content[:700])
        model = get_embedding_model(EMBEDDING_MODLE)
        embeddings = model.embed(texts)
        summary_embedding = model.embed([summary])[0]
        tmp_index = []
        for i, embedding in enumerate(embeddings):
            distance = cosine_distance(summary_embedding, embedding)
            tmp_index.append((topic_node[i], distance))
        tmp_index = sorted(tmp_index, key=lambda x: x[1], reverse=True)
        output_info = []
        for index, cosine in tmp_index:
            source_type = "issue"
            if "discuss.openubmc.cn" in topic_doc.loc[index]["url"]:
                source_type = "forum"
            output_info.append(
                {
                    "id": str(index),
                    "title": topic_doc.loc[index]["title"],
                    "url": topic_doc.loc[index]["url"],
                    "created_at": str(origin_data.loc[index]["created_at"]),
                    "source_type": source_type,
                    "source_id": str(origin_data.loc[index]["id"]),
                    "cosine": round(float(cosine), 3),
                }
                )
        topics[topic] = {
            "summary": summary,
            "discussion_count": len(topic_node),
            "discussion": output_info
        }
    # 保存为JSON文件
    with open('../data/topic_graph_info.json', 'w', encoding='utf-8') as f:
        json.dump(topics, f, ensure_ascii=False, indent=4)  # 确保中文字符正常显示
    # print(topics["5"])
    # print(topic_doc.loc[642])
    # print(topic_doc.loc[521])
