import pandas as pd
from datetime import datetime

# 读取Excel文件
input_file = "../data/openeuler_email_data.xlsx"
df = pd.read_excel(input_file)

filters = [
    {"column": "title", "pattern": r'例会|公示|公告|纪要|非问题|公式关闭|升级|会议|转测试|订阅|年报|月报|需求持续收集中|[PATCH]|提醒|进度报告|议题申报|提醒|告警|申请|说明|指南|议程'},
    {"column": "body", "pattern": r'邀请您参加|会议主题'}
]

filtered_df = df.copy()
dropped_samples = []

# 应用所有过滤条件
for condition in filters:
    mask = filtered_df[condition["column"]].str.contains(condition["pattern"], regex=True, na=False)
    dropped_samples.append(filtered_df[mask])
    filtered_df = filtered_df[~mask]

# 保存为新的Excel文件
excel_filename = f"../data/filtered_openeuler_email_data.xlsx"
filtered_df.to_excel(excel_filename, index=False)

print(f"原始数据条数: {len(df)}")
print(f"过滤后数据条数: {len(filtered_df)}")
print(f"过滤后的数据已保存至 {excel_filename}")
