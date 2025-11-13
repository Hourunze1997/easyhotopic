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
- Constrains: 文档应简洁、无同义词重复，适合社区开发者快速查阅。
- OutputFormat: 短小精悍的文字描述，直接且准确。
- Workflow:
  1. 提取需求核心要点。
  2. 去除同义词和冗余信息。
  3. 重组信息，形成简洁描述。
- Examples:
  - 例子1：openUBMC版本25.1.0需提供开发者指南，涵盖源码构建和API文档，供社区开发者使用。
"""

def llm_abstract(content):
    """使用LLM生成摘要"""
    start_time = time.time()
    openai_api_key = "sk-xxxxxx"
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

def pos_filter(text):
    words = pseg.lcut(text)
    # 保留名词、动词、形容词
    keep_pos = {'n', 'v', 'a'}  
    return [word for word, flag in words if flag[0] in keep_pos]

# 加载停用词表（建议组合多个来源）
def load_stopwords(paths):
    stopwords = defaultdict(int)
    for path in paths:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                stopwords[line.strip()] = 1
    return stopwords

# 使用哈工大、百度等停用词表
stopwords = load_stopwords(['../data/hit_stopwords.txt', '../data/baidu_stopwords.txt', '../data/self_stop.txt'])

def remove_stopwords(tokens):
    return [word for word in tokens if word not in stopwords and len(word) > 1]

def basic_clean(text):
    # 去除HTML标签
    text = re.sub(r'<.*?>', '', text)
    # 去除URL
    text = re.sub(r'https?://\S+', '', text)
    # 去除特殊符号（保留中文标点）
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9，。！？；：、]', ' ', text)
    return text.strip()

def format_issue_text(text):
    # 修正错别字
    text = re.sub(r'模版', '模板', text)
    
    # 处理日期格式（YYYY M D → YYYY/M/D）
    text = re.sub(r'(\d{4})\s+(\d{1,2})\s+(\d{1,2})', r'\1/\2/\3', text)
    
    # 删除中英文间多余空格
    text = re.sub(r'([\u4e00-\u9fff])\s+([a-zA-Z0-9])', r'\1\2', text)
    text = re.sub(r'([a-zA-Z0-9])\s+([\u4e00-\u9fff])', r'\1\2', text)
    
    # 处理中文标点后的空格
    text = re.sub(r'([：、。])\s+', r'\1', text)
    
    # 删除连续多余空格
    text = re.sub(r' +', ' ', text)
    
    # 优化段落格式（保留单空行分隔）
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # 对齐模板箭头格式
    text = re.sub(r'(\S+)\s+→\s+', r'\1 → ', text)
    
    return text.strip()

import re

def remove_na_content(text):
    # 使用正则表达式替换每行中NA及之后的内容
    return text.split("NA")[0]


def extract_issue_description(text):
    # 增强模式匹配多级标题结构
    patterns = [
        r'【修改描述】\s*(.+?)(?=\s*【|$)',
        r'【描述】\s*(.+?)(?=\s*【|$)',
        r'【任务描述一】\s*(.+?)(?=\s*【|$)',
        r'【任务描述二】\s*(.+?)(?=\s*【|$)',
        r'诉求：\s*(.+?)(?=\s*【|$)',
        r'(?i)(?:^|\n)#{1,3} 问题详细描述[^\n]*\n(.*?)(?=\n#{1,3} |\n\*\*|\n【|$)',
        r'(?i)(?:^|\n)#{1,3} 问题定位情况[^\n]*\n(.*?)(?=\n#{1,3} |\n\*\*|\n【|$)',
        r'(?i)(?:^|\n)#{1,3} 需求描述[^\n]*\n(.*?)(?=\n#{1,3} |\n\*\*|\n【|$)',
        r'(?i)(?:^|\n)#{1,3} 需求内容[^\n]*\n(.*?)(?=\n#{1,3} |\n\*\*|\n【|$)',
        r'【简要说明】\s*(.*?)(?=\n【|\n$|\n#)',
        r'【问题详细描述】：\s*(.*?)(?=\n【|\n$|\n#)',
        r'【问题定位情况】\s*：\s*((?:.|\n)+?)(?=\n\s*【|\Z)',
        r'(?i)(?:^|\n)#{1,3} 简要说明[^\n]*\n(.*?)(?=\n#{1,3} |$)',
    ]

    # 清理HTML注释和空标题
    cleaned_text = re.sub(r'<!--.*?-->|\n#.*\n+$', '', text, flags=re.DOTALL)
    res = []
    # 多层内容提取
    for pattern in patterns:
        match = re.search(pattern, cleaned_text, re.DOTALL)
        if match:
            content = match.group(1).strip()
            # 过滤无效内容
            valid_lines = [
                line for line in content.split('\n')
                if line.strip()
                   and not re.match(r'^(NA|（NA）|#+|【)', line.strip())
            ]
            if valid_lines:
                res.extend(valid_lines)
    if res:
        return "\n".join(res)
    return text


def clean_issue_text(text):
    content = extract_issue_description(text)
    content = basic_clean(content)
    res = format_issue_text(content)
    res = remove_na_content(res)
    res = llm_abstract(res)
    return res

def clean_title(title):
    # 保留汉字、字母、数字、逗号句号，新增去除【】[]
    return re.sub(
        r'[^\w\u4e00-\u9fff,，.。]|[\u3010\u3011\[\]\u300A\u300B()]',  # 匹配特殊字符
        ' ',  # 替换为空格而不是空字符串
        str(title)
    )


def process_excel(input_path='openubmc_issue.xlsx', output_path='processed_issues.xlsx'):
    """处理Excel文件并生成新文件"""
    # 读取原始Excel文件
    df = pd.read_excel(input_path)

    # 新增处理列（假设原始数据在'body'列）
    df['processed_body'] = df['body'].apply(clean_issue_text)

    # 保存到新文件
    df.to_excel(output_path, index=False)


def chinese_segment(text):
    # 使用jieba精确模式分词
    seg_list = jieba.lcut(text, cut_all=True, use_paddle=True, HMM=True)
    return seg_list

# 添加文件处理示例（可根据需要调用）
if __name__ == "__main__":
    # 处理Excel文件
    process_excel(input_path="../data/openubmc_issue_open.xlsx", output_path="../data/processed_issues_open.xlsx")
    print("处理完成，结果已保存到 processed_issues_open.xlsx")
#     content = """
#     问题背景：

# 1、当前资源树协作接口关键字使用范围不明确，导致社区开发者以及interface-sig组在评审和维护资源树协作接口时缺少评审和看护标准

# 2、存在组件模型定义和资源树协作接口定义不一致问题：

# 组件模型对属性的约束范围与资源树协作接口属性的约束范围不一致：可能导致开发者基于资源树协作接口开发的属性设置功能与预期不符，例如minLength、maxLength， 接口定义[10, 20]，实现范围[10, 15]。

# 组件模型约定的组件内部实现暴露到资源树协作接口：可能影响开发者基于资源树协作接口的组件二次开发，例如usage、refInterface

# 因此需要对组件模型定义和资源树协作接口进行优化
#     """
#     # tests = pos_filter(tests)
#     # print(tests)
#     # print(chinese_segment(tests))
#     tests = clean_issue_text(content)
#     print(tests)
