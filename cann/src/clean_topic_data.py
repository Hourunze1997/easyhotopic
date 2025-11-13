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
- Constrains: 文档应简洁、无同义词重复，适合社区开发者快速查阅, 体现title内容。
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
  - 例子1: 事件定制开发中遇到的问题: 按照社区上的事件定制做了开发，但没有实现对应的告警事件，发帖求助过。 详见该帖, 如何配置自定义事件, 有伙伴回答是要配置在vendor/event_def.json当中，后续也尝试在该文件中添加了定义，还是没有实现告警。
"""

def llm_abstract(content):
    """使用LLM生成摘要"""
    start_time = time.time()
    openai_api_key = "sk-xxxxxxx"
    openai_api_base = "https://api.siliconflow.cn/v1"
    client = OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base,
    )
    chat_outputs = client.chat.completions.create(
        model="Qwen/Qwen3-32B",
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
    process_excel(input_path="../data/cann_forum_topics_without_solved.xlsx", output_path="../data/processed_forum_topics.xlsx")
    print("处理完成，结果已保存到 processed_forum_topics.xlsx")
    # title = "Atlas 500 A2使用OpenCV报错：driver error feature not support"
    # body = """
    # 我在Atlas 500 A2上创建了一个docker容器，在容器内部安装了Ascend-cann-toolkit_7.0.0_linux-aarch64和算子包Ascend-cann-kernels-310b_7.0.0_linux，然后编译了带cannops模块的OpenCV4.10.0，最后运行示例程序的时候报错： terminate called after throwing an instance of 'cv::Exception' what():  OpenCV(4.10.0) /home/opencvcompile/opencv_contrib-4.10.0/modules/cannops/src/cann_call.cpp:97: error: (-2:Unspecified error) in function 'aclrtMemcpy2dWarpper' &gt; EL0014: The operation is unsupported. &gt;         TraceBack (most recent call last): &gt;         rtMemcpy2d execute failed, reason=[driver error:feature not support][FUNC:FuncErrorReason][FILE:error_message_manage.cc][LINE:50] &gt;         [Synchronized][Memcpy]synchronized memcpy failed, kind = 1, runtime result = 207000[FUNC:ReportCallError][FILE:log_inner.cpp][LINE:161] &gt; Aborted 似乎是因为该驱动版本不支持其中的某个函数？我在网上找不到相关的内容，有人知道OpenCV和CANN、驱动的版本对应关系吗？是因为Atlas 500 A2芯片310b不支持吗？
    # """

    # input = f"""
    # - title: {title}
    # - body: {body}
    # """
    # res = llm_abstract(input)
    # print(res)
