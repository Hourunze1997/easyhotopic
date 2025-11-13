import re
import pandas as pd
import jieba
from collections import defaultdict
import jieba.posseg as pseg
from openai import OpenAI
import time

system_prompt = """
- Role: 开源昇腾CANN社区领域专家
- Profile: 对issue和论坛内容非常熟悉，能够高效地提炼关键信息，去除冗余内容。
- Skills: 你具备信息提取能力，能够快速理解和简化复杂的输入内容 {content}。
- Constrains: 文档应简洁、无同义词重复，适合社区开发者快速查阅, 体现title内容, 无法识别时直接返回tilte内容。
- input:
  - title: 问题标题
  - body: 问题描述
- OutputFormat: 短小精悍的文字描述，直接且准确。
- Workflow:
  1. 提取需求核心要点。
  2. 去除同义词和冗余信息。
  3. 重组信息，形成简洁描述。
  4. 与title内容相关联
- Examples:
  - 例子1: 使用上述ATC指令把算子转换成om模型，在加载的时候会出现500002出错码，加载由prototxt转出的om模型可以正常加载。请问如何解决这个问题。
  - 例子2: 算子使能到模型后性能降低: 原生torch接口性能最佳，torch_act 与 torch.ops.Act性能较差, 当前算子是否在模型中有加速效果, 如何在模型中进行加速（给出的用例的方法是否可取), 在模型层面 如何 无感 进行算子替换？
"""

def llm_abstract(content):
    """使用LLM生成摘要"""
    start_time = time.time()
    openai_api_key = "sk-xxxx"
    openai_api_base = "https://api.siliconflow.cn/v1"
    # openai_api_key = "xxxxxxx"
    # openai_api_base = "https://ai.gitee.com/v1"
    client = OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base,
    )
    chat_outputs = client.chat.completions.create(
        model="Qwen/Qwen3-32B",
        # model="Qwen3-32B",
        # enable_thinking=False,
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

def basic_clean(text):
    # 去除HTML标签
    text = re.sub(r'<.*?>', '', text)
    # 去除特殊符号（保留中文标点）
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9，。！？；：、]', ' ', text)
    return text.strip()

def clean_text(text):
    res = llm_abstract(text)
    content = basic_clean(res)
    return content

def process_excel(input_path='openubmc_issue.xlsx', output_path='processed_issues.xlsx'):
    """处理Excel文件并生成新文件"""
    # 读取原始Excel文件
    df = pd.read_excel(input_path, engine='openpyxl')
    processed_body = []
    for _, row in df.iterrows():
        title = row['title']
        body = row['body']
        content = f"- title: {title}\n- body: {body}"
        res = clean_text(content)
        # print(f"processed_body: {res}")
        processed_body.append(res)

    df['processed_body'] = processed_body

    # 保存到新文件
    df.to_excel(output_path, index=False)

if __name__ == "__main__":
    process_excel(input_path="../data/cleaned_cann_issue.xlsx", output_path="../data/processed_issues_new.xlsx")
    print("处理完成，结果已保存到 processed_issues_new.xlsx")
#     content = """
# cann7.1又支持的torchair版本吗
# """
#     title = "cann7.1又支持的torchair版本吗"
#     input = f"""
#     - title: {title}
#     - body: {content}
#     """
#     result = clean_text(content)
#     print(result)
