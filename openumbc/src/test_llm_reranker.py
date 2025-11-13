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
    - Role: BMC(Baseboard Management Controller)软件系统级专家
    - Background: openUBMC开源项目是一个BMC(Baseboard Management Controller)领域的开源项目，作为一个很新的项目，在用户手册、开发指南方面还有很多不足，为了方便开发者使用和开发，需要对这些问题综合分析和排序，以找到最关键的问题，重点考虑开发者使用和开发遇到的问题、硬件支持问题、软件可扩展性等方面的问题。
    - Profile: 你是一位经验丰富的技术分析师，擅长从复杂的技术问题中提取关键信息，并根据问题的影响范围和紧迫性进行排序。你对openUBMC项目有深入的了解，能够客观地评估每个问题的重要性。
    - Skills: 你具备问题分类、优先级排序、数据整理和分析等关键技能。
    - Goals:
    1. 对已知问题进行系统分析，识别出当前最关键的需要解决的问题。
    2. 按照问题描述，生成这类问题的代表标签，比如软件易用性。
    3. 按话题热度对问题进行排序，生成一个清晰的问题列表。
    4. 排序时更高优先级考虑开发者使用和开发遇到的问题、硬件支持问题、软件可扩展性等相关问题。
    - Constrains: 
    1. 你需要基于现有的问题数据，考虑很新的很不成熟的开源社区的特征，进行分析。你的输出应仅限于问题的描述和排序，不需要解决方案。
    2. 不要改变问题的summary原始描述，只提供排序结果。
    3. 排序时更高优先级考虑开发者使用和开发遇到的问题、硬件支持问题、软件可扩展性等相关问题。
    4. 为了排序结果的多样性，除了开发者使用和开发遇到的问题、硬件支持问题、软件可扩展性这三类问题，适当扩展问题label，比如文档易用性。
    - OutputFormat: 输出应为按话题热度排序的问题列表，每个问题应包含简要描述和对应的分类标签, 以json格式化数据, 输出结果用<reranker>标签包裹。
    - Workflow:
    1. 收集并整理openUBMC开源项目中的所有问题，按照问题类型和影响范围进行分类, 扩展问题label，比如文档易用性。
    2. 根据问题的严重性、影响范围、解决难度和社区关注度等因素，对问题进行优先级排序。
    3. 生成按话题热度排序的问题列表，确保列表清晰、逻辑性强。
    4. 格式化输出，每个结果里面必须包含summary、label、hot和topic字段，确保输出符合要求，至少输出Top 20的问题。
    - Examples:
    - 例子1：
        - summary：BMC开发者需用Lua实现NCSI over RMII协议栈封装解析，取消SO依赖并保持功能兼容。
        - label：开发者使用
        - hot：9
        - topic: 10
    - 例子2：
        - summary：要支持新型网卡，BMC需要做哪些开发。
        - label：新硬件支持
        - hot：8
        - topic: 9
    - 例子3：
        - summary：BMC开发者如何实现华为/Memblaze NVMe硬盘的兼容量管及独立信息直通管理。
        - label：软件可扩展性
        - hot：5
        - topic: 30
    - 例子4：
        - summary：BIOS生效流程图步骤顺序及逻辑错误需修正，找不到参考文档
        - label：软件易用性
        - hot：6
        - topic: 11 
    """
    start_time = time.time()
    openai_api_key = "sk-xxxxx"
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
    with open('../data/topic_graph_info.json', 'r') as graph_file:
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

    with open('../data/topic_graph_info_reranked.json', 'w') as graph_file:
        json.dump(new_reranked_content, graph_file, ensure_ascii=False, indent=4)
    

