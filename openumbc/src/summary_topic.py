import requests
import json
import pandas as pd
from tqdm import tqdm
from openai import OpenAI
import time

def llm_summary(content):
    system_prompt = f"""
    - Role: 专业的BMC专家和技术文档分析专家
    - Background: 用户需要从提供的文档内容中提炼出BMC领域开发者关心或亟需解决的核心问题，这表明用户可能正在处理与BMC相关的技术文档，需要快速准确地提取关键信息以指导开发工作。
    - Profile: 你是一位在BMC（Baseboard Management Controller，基板管理控制器）领域拥有深厚专业知识的专家，同时也擅长技术文档的分析和解读，能够精准地识别出文档中对开发者具有重要意义的问题。
    - Skills: 你具备对BMC技术的全面理解，包括硬件架构、固件开发、协议交互等，以及对技术文档的深度分析能力，能够快速定位关键信息并提炼出核心问题。
    - Goals: 从提供的文档内容中精准提炼出BMC领域开发者关心或亟需解决的核心问题。
    - Constrains: 问题表述需聚焦具体操作场景，包含明确技术主体，体现受众，字数控制在30以内，采用陈述句呈现，返回结果用<summary>标签包裹。
    - OutputFormat: 一句话，用<summary>标签包裹。
    - Workflow:
    1. 仔细阅读并理解提供的文档内容，识别与BMC开发相关的部分。
    2. 确定文档中涉及的具体操作场景和明确技术主体。
    3. 根据BMC开发者的视角，提炼出亟需解决的核心问题，并确保表述符合要求。
    4. 返回结果，保证只有一个<summary>标签包裹，结果覆盖共性描述。
    - Examples:
    - 例子1：BMC固件升级中如何确保硬件兼容性
    - 例子2：BMC开发者如何优化固件性能
    - 例子3：BMC固件开发中如何避免硬件兼容性缺陷
    """
    start_time = time.time()
    openai_api_key = "sk-xxxx"
    openai_api_base = "https://api.siliconflow.cn/v1"
    client = OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base,
    )
    chat_outputs = client.chat.completions.create(
        model="Qwen/Qwen3-235B-A22B",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ]
    )
    # print(chat_outputs.choices[0].message.content)
    end_time = time.time()
    elapsed_time= end_time - start_time
    print(f"exec time: {elapsed_time} s")
    return chat_outputs.choices[0].message.content

def merge_keywords(data):
    merged_keywords = {}
    for group_id, keyword_lists in data.items():
        # Flatten the list of lists into a single list of keywords
        all_keywords = [keyword for keyword_list in keyword_lists for keyword in keyword_list]
        # Remove duplicates by converting to a set and back to a list
        unique_keywords = list(set(all_keywords))
        merged_keywords[group_id] = unique_keywords

    return merged_keywords

def process_csv():
    input_file = "../data/topic_docs_merged_new.xlsx"
    tpoic_path = "../data/topic_info_merged_new.xlsx"
    output_file = "../data/topic_output_merged_new.xlsx"
    topics = {}
    hot_keys = {}
    topic_info = pd.read_excel(tpoic_path)
    for _, row in topic_info.iterrows():
        topic = str(row['Topic'])
        if topic == '-1':
            continue
        if topic not in topics:
            hot_keys[topic] = []
        hot_keys[topic].append((row['Aspect1'], row['Aspect1']))

    hot_keys = merge_keywords(hot_keys)
    print(hot_keys)
    df = pd.read_excel(input_file)
    for _, row in df.iterrows():
        topic = str(row['Topic'])
        if topic == '-1':
            continue
        if topic not in topics:
            topics[topic] = []
        topics[topic].append((row['Probability'], row['Document']))

    for topic in topics:
        topics[topic] = [content for _, content in sorted(
            topics[topic],
            key=lambda x: x[0],
            reverse=True
        )]
    # print(topics)
    summaries = {}
    with tqdm(topics.items(), desc="📊 处理进度", unit="topic", bar_format="{l_bar}{bar:20}{r_bar}") as pbar:
        for topic, contents in pbar:
            min_cluster = 15
            content_block = "\n".join(contents[:min_cluster])
            print(topic, len(contents), hot_keys[topic])
            hot_keys_topic = hot_keys[topic]
            content = f"""
            以下是社区关于该热点话题的关键词和部分内容：
            关键词：{hot_keys_topic}
            内容：{content_block}
            """
            # print(content)
            llm_summary_result = llm_summary(content)
            print(llm_summary_result)
            if '<summary>' in llm_summary_result:
                summary = llm_summary_result.split('<summary>')[1].split('</summary>')[0].strip()
                summaries[topic] = summary
    df['summary'] = df['Topic'].astype(str).apply(lambda x: summaries.get(x, ''))
    df.to_excel(output_file, index=False)
    topic_info['summary'] = topic_info['Topic'].astype(str).apply(lambda x: summaries.get(x, ''))
    topic_info.to_excel(tpoic_path, index=False)

if __name__ == "__main__":
    process_csv()
    # input_file = "../data/topic_docs_merged.xlsx"
    # df = pd.read_excel(input_file)
    # tpoic_path = "../data/topic_info_merged.xlsx"
    # topic_info = pd.read_excel(tpoic_path)
    # summaries = {}
    # for _, row in topic_info.iterrows():
    #     topic = str(row['Topic'])
    #     summary = row['summary']
    #     summaries[topic] = summary
    # print(summaries)
    # output_file = "../data/topic_output_merged.xlsx"
    # df['summary'] = df['Topic'].astype(str).apply(lambda x: summaries.get(x, ''))
    # df.to_excel(output_file, index=False)
