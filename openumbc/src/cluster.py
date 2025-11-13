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

API_KEY = "sk-xxxxxxx"
BASE_URL = "https://api.siliconflow.cn/v1"
# EMBEDDING_MODLE = "BAAI/bge-m3"
EMBEDDING_MODLE = "BAAI/bge-large-zh-v1.5"
# EMBEDDING_MODLE = "netease-youdao/bce-embedding-base_v1"

def get_origin_data(path):
    df = pd.read_excel(path, sheet_name="Sheet1") 
    return df

class CustomEmbedder(BaseEmbedder):
    def __init__(self):
        super().__init__()

    def text_embedding(self, doc):
        url = "https://ainference.osinfra.cn/v1/embeddings"
        payload = {
            "model": "jina-embeddings-v3",
            "input": doc,
            "encoding_format": "float"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
                raise Exception(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error: {e}")
            raise Exception(f"{response.text}")
    
        # print(response.text)
        return response.json().get("data")[0].get("embedding")

    def encode(self, documents):
        embeddings = []
        for input in documents:
            output = self.text_embedding(input)
            embeddings.append(output)
        return np.array(embeddings)

    def embed(self, documents, verbose=False):
        return self.encode(documents)

def get_embedding_model(model_name):
    client = openai.OpenAI(api_key=API_KEY, base_url=BASE_URL)
    embedding_model = OpenAIBackend(client, model_name, batch_size=32)
    return embedding_model
    # embedding_model = CustomEmbedder()
    # return embedding_model


def calculate_embeddings(texts, model_name):
    client = openai.OpenAI(api_key=API_KEY, base_url=BASE_URL)
    embedding_model = get_embedding_model(model_name)
    embeddings = embedding_model.embed(texts)
    return embeddings

def get_bert_topic_model(n_clusters=20):
    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine', random_state=42)
    hdbscan_model = HDBSCAN(min_cluster_size=n_clusters, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
    def tokenize_zh(text):
        words = jieba.lcut(text)
        return words
    vectorizer_model = CountVectorizer(stop_words=['需求', '问题', "失败", "错误", "title", "body"], min_df=3, ngram_range=(1, 3), tokenizer=tokenize_zh)
    # KeyBERT
    keybert_model = KeyBERTInspired()
    # aspect_model1 = PartOfSpeech("en_core_web_sm")
    aspect_model1 = PartOfSpeech("zh_core_web_sm")
    aspect_model2 = [KeyBERTInspired(top_n_words=30), MaximalMarginalRelevance(diversity=.5)]
    # Add all models together to be run in a single `fit`
    representation_model = {
        "Main": keybert_model,
        "Aspect1":  aspect_model1,
        "Aspect2":  aspect_model2
    }
    ctfidf_model = ClassTfidfTransformer(
    seed_words=["资源协作接口", "D-Bus", "Path", "Interface", "Property and Method", "设备管理接口",
                "DDS", "设备管理驱动", "CMake", "Conan", "bingo", "BMCStudio", "Skynet", "openUBMC SDK",
                "CLI", " SNMP", " SEL", " SDR", " IPMI", "Redfish", "持久化", "MDS", "微组件框架", "CSR", "硬件自发现"],
    seed_multiplier=2,
    reduce_frequent_words=True
)

    embedding_model = get_embedding_model(EMBEDDING_MODLE)

    topic_model = BERTopic(
        # Pipeline models
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer_model,
        representation_model=representation_model,
        ctfidf_model=ctfidf_model,
        # Hyperparameters
        top_n_words=20,
        verbose=True
    )

    return topic_model

def calculate_topics(texts, model_name, origin_df, n_clusters=10):
    topic_model = get_bert_topic_model(n_clusters)
    embeddings = calculate_embeddings(texts, model_name)
    topics, probs = topic_model.fit_transform(texts, embeddings)

    topic_docs = topic_model.get_document_info(texts)
    topic_docs['url'] = origin_df['url']
    topic_docs['title'] = origin_df['title']
    topic_docs['body'] = origin_df['body']
    topic_docs.to_excel('../data/topic_docs_merged_new.xlsx', sheet_name="sheet1", index=False, engine="openpyxl")
    print('topic_docs shape：', topic_docs.shape)

    topic_info = topic_model.get_topic_info()
    topic_info.to_excel('../data/topic_info_merged_new.xlsx', sheet_name="sheet1", index=False, engine="openpyxl")
    print('topic_info shape：', topic_info.shape)

    return topics, probs

def basic_clean(text):
    # 去除HTML标签
    text = re.sub(r'<.*?>', '', text)
    # 去除特殊符号（保留中文标点）
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9，。！？；：、]', '', text)
    return text.strip()

if __name__ == "__main__":
    df = get_origin_data('../data/merged_issue_forum_new.xlsx')
    df = df.fillna('')
    texts = []
    for _, row in df.iterrows():
        title = basic_clean(row['title'])
        body = row['processed_body']
        content = f"- title: {title}\n- body: {body}"
        content = content[:700]
        texts.append(content)
        
    topics, probs = calculate_topics(texts, EMBEDDING_MODLE, df)
    print(topics)
    print(probs)

