import pandas as pd
import numpy as np
import pandas as pd
import openai
from bertopic.backend import OpenAIBackend
import numpy as np
import json
from openai import OpenAI
import time

def llm_reranker(content):
    system_prompt = f"""
    - Role: 专业的昇腾CANN（类似Nvidia CUDA）系统级技术专家、Ascend C系统及技术专家
    - Background: 昇腾Ascend C和CANN（类似Nvidia CUDA）社区在用户手册、开发指南方面还有很多不足，为了弥补这方面的不足，需要对这些问题综合分析和排序，以找到最关键的问题，重点考虑开发者使用软件遇到的问题、开发融合算子或基础算子的问题、软件易用性问题。
    - Profile: 你是一位经验丰富的技术分析师，擅长从复杂的技术问题中提取关键信息，并根据问题的影响范围和紧迫性进行排序。你对昇腾Ascend C和CANN（类似Nvidia CUDA）有系统的了解，能够评估每个问题的重要性。
    - Skills: 你具备问题分类、优先级排序、数据整理和分析等关键技能。
    - Goals:
    1. 对已知问题进行系统分析，识别出当前最紧迫的热点问题。
    2. 按照热点问题描述，生成这类问题的代表标签，比如软件易用性。
    3. 按话题热度对问题进行排序，生成一个清晰的问题列表。
    4. 排序时更高优先级考虑开发者使用、开发者开发、软件易用性等相关问题。
    - Constrains: 
    1. 你需要基于现有的问题数据，对比Nvidia CUDA软件和社区，识别重点问题。你的输出应仅限于问题的描述和排序，不需要解决方案。
    2. 不要改变问题的summary原始描述，只提供排序结果。
    - OutputFormat: 输出应为按问题紧迫度排序的问题列表，每个问题应包含简要描述和对应的分类标签, 以json格式化数据, 输出结果用<reranker>标签包裹。
    - Workflow:
    1. 收集并整理昇腾Ascend C和CANN中的所有问题，首先识别有提问但没有得到有效答复的问题，归类为“答复走肾不走心”。
    2. 对剩余的问题按照问题类型和影响范围进行分类, 扩展问题label，比如软件易用性。
    3. 根据问题的严重性、影响范围、解决难度和社区关注度等因素，对问题进行优先级排序。
    4. 生成按话题热度排序的问题列表，确保列表清晰、逻辑性强。
    5. 格式化输出，每个结果里面必须包含summary、label、hot和topic字段，确保输出符合要求，至少输出Top 20的问题。
    - Examples:
    - 例子1：
        - summary：xxxxxxx
        - label：开发融合算子问题
        - hot：9
        - topic: 1
    - 例子2：
        - summary：xxxxxxxx
        - label：软件易用性
        - hot：8
        - topic: 2
    """
    start_time = time.time()
    openai_api_key = "sk-xxx"
    openai_api_base = "https://api.siliconflow.cn/v1"
    client = OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base,
    )
    chat_outputs = client.chat.completions.create(
        # model="Qwen/Qwen3-235B-A22B",
        # model="Pro/deepseek-ai/DeepSeek-R1",
        model="deepseek-ai/DeepSeek-R1",
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

if __name__ == "__main__":
    reranked_content = ""
    with open('../data/topic_graph_info_2025_1_1.json', 'r', encoding='utf-8') as graph_file:
        graph_data = json.load(graph_file)
        tmp_texts = ""
        for topic, info in graph_data.items():
            summary = info.get("summary", "")
            # print(f"Topic: {topic}\nSummary: {summary}")
            tmp_texts += f"Topic: {topic}\nSummary: {summary}\n"
            tmp_texts += "Discussions:\n"
            discussion = info.get("discussion", [])
            # print(f"Discussion Count: {discussion}")
            discussion_text = ""
            for i, doc in enumerate(discussion):
                discussion_text += f"{i+1}. {doc['title']}\n"
            tmp_texts += discussion_text
            tmp_texts += "\n"
        # print(tmp_texts)
        reranked_content = llm_reranker(tmp_texts)
        # print(f"Topic: {topic}\nReranked Content: {reranked_content}\n")
    
    if "<reranker>" in reranked_content:
        reranked_content = reranked_content.split("<reranker>")[1].split("</reranker>")[0]
    print(f"Reranked Content: {reranked_content}\n")
    reranked_content = json.loads(reranked_content)
    new_reranked_content = {}
    new_index = 0
    for index, item in enumerate(reranked_content):
        # print(f"Reranked Item: {item}\n")
        topic_id = index
        origin_id = item.get("topic")
        if not origin_id:
            continue
        content = graph_data.get(str(origin_id), {})
        if not content:
            continue
        content["label"] = item.get("label", "")
        # print(f"summary: {content.get('summary', '')}, item summary: {item.get('summary', '')}")
        new_reranked_content[str(new_index)] = content
        new_index += 1
        del graph_data[str(origin_id)]
    # print(f"Reranked Content Length: {new_reranked_content}")
    for index, item in enumerate(graph_data):
        content = graph_data.get(str(item), {})
        if not content:
            continue
        new_reranked_content[str(new_index)] = content
        new_index += 1

    with open('../data/topic_graph_info_reranked_2025_1_1.json', 'w', encoding='utf-8') as graph_file:
        json.dump(new_reranked_content, graph_file, ensure_ascii=False, indent=4)
    

