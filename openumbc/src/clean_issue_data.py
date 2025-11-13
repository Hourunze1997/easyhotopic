import re
import pandas as pd
import jieba
from collections import defaultdict
import jieba.posseg as pseg
from openai import OpenAI
import time

system_prompt = """
- Role: 开源openUBMC社区领域专家
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
  - 例子1: JTAG DFT测试项目，硬件JTAG链路断开，JTAG DFT测试项依然PASS。
  - 例子2: 功耗封顶加固需求: 新增电源功耗获取CRC校验, 支持ScanStatus属性实时刷新监控。
"""

def llm_abstract(content):
    """使用LLM生成摘要"""
    start_time = time.time()
    openai_api_key = "sk-xxxxx"
    openai_api_base = "https://api.siliconflow.cn/v1"
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
    df = pd.read_excel(input_path)
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
    process_excel(input_path="../data/openubmc_issue_open.xlsx", output_path="../data/processed_issues_new.xlsx")
    print("处理完成，结果已保存到 processed_issues_new.xlsx")
    # with open("../data/社区系统需求提交模版.md", "r", encoding="utf-8") as f:
    #     template1 = f.read()
    # with open("../data/社区组件需求提交模板.md", "r", encoding="utf-8") as f:
    #     template2 = f.read()
    # with open("../data/社区问题单提交模板.md", "r", encoding="utf-8") as f:
    #     template3 = f.read()
    # print(template1)
#     content = """
#     【简要说明】功耗封顶加固
# 【系统用户】开发人员
# 【前置条件】BMC运行正常
# 【主成功场景】功耗封顶成功，包含
# 1、新增电源功耗获取CRC校验
# 2、支持ScanStatus属性实时刷新监控
# 【扩展场景(含异常场景)】NA
# 【约束】NA
# 【非功能需求】
# （1）可靠性要求：NA
# （2）可维护性要求：NA
# （3）可测试性要求：NA
# （4）性能要求：NA
# （5）兼容性要求(和以前版本及周边配套)：NA
# （6）安全要求：NA
# （7）韧性要求：NA
# """
#     title = "【需求】功耗封顶加固"
#     input = f"""
#     - title: {title}
#     - body: {content}
#     """
#     result = clean_text(content)
#     print(result)
    # result = llm_clean_template(content)
    # print(result)
