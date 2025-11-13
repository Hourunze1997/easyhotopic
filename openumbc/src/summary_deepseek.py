import csv
import requests
import json
import pandas as pd
from tqdm import tqdm


sk_token = 'sk-'
model = "Qwen/Qwen3-235B-A22B"


def process_csv(input_file, output_file):
    topics = {}

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
    # 准备API请求参数
    api_url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {sk_token}",
        "Content-Type": "application/json"
    }

    # 处理每个topic
    summaries = {}
    with tqdm(topics.items(), desc="📊 处理进度", unit="topic", bar_format="{l_bar}{bar:20}{r_bar}") as pbar:
        for topic, contents in pbar:
            print(topic, len(contents))
            # 构造prompt内容
            content_block = "\n".join(contents[:10])
            prompt = f"""
            请基于以下文档内容：{content_block}，用一句话精准提炼BMC领域开发者关心或亟需解决的核心问题。
            要求问题表述：1）聚焦具体操作场景 2）包含明确技术主体 3）体现受众 4) 字数控制在30以内 5) 采用陈述句呈现 6) 返回结果用<summary>标签包裹。
            参考示例：
            1. 如何确定开源社区维护者应优先更新的API兼容性文档清单
            2. BMC固件开发团队需要哪些标准化调试工具集成指南
            3. 多厂商BIOS协议交互时存在哪些特定硬件兼容性缺陷"""

            system_prompt = f"""你是一个专业的BMC专家和技术文档分析专家。"""

            pbar.set_postfix_str(f"Topic: {topic} | 文本数: {len(contents)}", refresh=False)

            # 调用API
            try:
                response = requests.post(
                    api_url,
                    headers=headers,
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}, {"role": "system", "content": system_prompt}],
                    },
                    timeout=300
                )
                response.raise_for_status()

                # 提取summary内容
                result = json.loads(response.text)
                summary = result['choices'][0]['message']['content']
                if '<summary>' in summary:
                    summary = summary.split('<summary>')[1].split('</summary>')[0].strip()
                summaries[topic] = summary
            except Exception as e:
                print(f"处理topic '{topic}'时出错: {str(e)}")
                summaries[topic] = "总结生成失败"


    with open('../output/summary.txt', 'w', encoding='utf-8') as f:
        # 生成带缩进的JSON格式
        f.write("{\n")
        for i, (k, v) in enumerate(sorted(summaries.items(), key=lambda x: int(x[0]))):
            f.write(f'    "{k}": "{v}"')
            if i < len(summaries) - 1:
                f.write(",")
            f.write("\n")
        f.write("}")
    # 写入新CSV文件
    df = pd.read_excel(input_file)
    df['summary'] = df['Topic'].astype(str).apply(lambda x: summaries.get(x, ''))
    df.to_excel(output_file, index=False)


if __name__ == "__main__":
    process_csv('../data/topic_docs.xlsx', '../output/output.xlsx')
