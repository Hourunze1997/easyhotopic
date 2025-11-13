import json

import pandas as pd
import re

import requests

sk_token = ''


def clean_title(title):
    # 保留汉字、字母、数字、逗号句号，新增去除【】[]
    return re.sub(
        r'[^\w\u4e00-\u9fff,，.。]|[\u3010\u3011\[\]\u300A\u300B()]',  # 匹配特殊字符
        ' ',  # 替换为空格而不是空字符串
        str(title)
    )


def process_abstract(content):
    """处理摘要，保留汉字、字母、数字、逗号句号，去除多余空格"""
    # 保留汉字、字母、数字、逗号句号，去除多余空格
    prompt = f"""
    请为以下长文本生成1000字内的简洁摘要：
    - 用连贯段落呈现核心内容
    - 保持客观并涵盖主要信息
    - 无需分点/小标题/特殊格式
    ===内容开始===
    {content}
    ===内容结束===
    """
    api_url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {sk_token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(
            api_url,
            headers=headers,
            json={
                "model": "Qwen/Qwen3-235B-A22B",
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=300
        )
        response.raise_for_status()
        result = json.loads(response.text)
        abstract = result['choices'][0]['message']['content']
        return clean_title(abstract)
    except Exception as e:
        return "摘要生成失败"


def process_input(row):
    print(row['title'])
    input_text = row['title'] + ' ' + row['body']
    return process_abstract(input_text)

# 读取两个源文件
df1 = pd.read_excel('forum_topics.xlsx', engine='openpyxl')
df2 = pd.read_excel('openubmc_issue.xlsx', engine='openpyxl')

df1['text'] = df1.apply(process_input, axis=1)
df2['text'] = df2.apply(process_input, axis=1)

# 合并两个列数据
combined2 = df1['text'].tolist() + df2['text'].tolist()
combined3 = df1['url'].tolist() + df2['html_url'].tolist()


# 创建新DataFrame并保存
pd.DataFrame({
    'input': combined2,
    'url': combined3,
    'body_length': [len(str(text)) for text in combined2]
}).to_excel('../output/all_text_url.xlsx', index=False)

