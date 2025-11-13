import pandas as pd
import json

# 读取 Excel 文件
file_path = '../data/openUBMC-20250530-release.xlsx'  # 请替换成您的文件路径
df = pd.read_excel(file_path, header=None)

# 初始化变量
topics_dict = {}
url_dict = {}

def get_topic_dict():
    current_topic = None
    # 遍历 Excel 数据行
    for index, row in df.iterrows():
        # 如果行的第一个单元格值为“话题描述”，则获取话题描述并初始化相关讨论源列表
        if row[0] == '话题描述' and pd.notna(row[1]):
            current_topic = row[1]
            topics_dict[current_topic] = []
        
        if pd.isna(row[0]) and pd.notna(row[1]) and pd.notna(row[2]):
            # 如果行的第一个单元格为空，但第二个单元格不为空，则继续处理当前话题
            # print(f"处理当前话题: {current_topic}, 内容: {row[1]}")
            topics_dict[current_topic].append({
                    'title': row[1],
                    'url': row[2]
                })
            url_dict[row[2]] = {'title': row[1], 'topic': current_topic}
        

if __name__ == "__main__":
    get_topic_dict()
    origin_data = pd.read_excel('../data/merged_issue_forum_new.xlsx', sheet_name="Sheet1")
    topics_summary = []
    for _, row in origin_data.iterrows():
        row_url = row['url']
        content = url_dict.get(row_url, None)
        if not content:
            topics_summary.append("")
            continue
        else:
            title = content['title']
            if title != row['title']:
                print(f"标题不一致: {title} != {row['title']}")
                topics_summary.append("")
                continue
            topics_summary.append(f"{content["topic"]}")
    # get_release_topic.py -> deal_old_data.py -> generate_graph_node.py -> generate_graph_cluster.py 
    # -> summary_graph_topic.py -> merge_cluster_result.py -> test_convert_graph_output.py -> test_llm_reranker.py
    origin_data['topic'] = topics_summary
    new_data = pd.read_excel('../data/merged_issue_forum_new_0605.xlsx', sheet_name="Sheet1")
    origin_data = pd.concat([origin_data, new_data], ignore_index=True)
    origin_data.to_excel('../data/merged_issue_forum_release_new.xlsx', index=False, engine='openpyxl')
       

# # 将数据输出为 JSON 文件
# output_file = '../data/openUBMC-20250530-release.json'  # 输出的 JSON 文件路径
# with open(output_file, 'w', encoding='utf-8') as json_file:
#     json.dump(topics_dict, json_file, ensure_ascii=False, indent=4)

# print(f'JSON 数据已成功写入到 {output_file}')
