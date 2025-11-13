import pandas as pd
from datetime import datetime

# 读取Excel文件
input_file = "../data/mindspore_forum_data.xlsx"
df = pd.read_excel(input_file)

filters = [
    {"column": "title", "pattern": r'指南|干货小卖部|开发者说|课程|体验|0day同步！|扩散模型'},
]

filtered_df = df.copy()
dropped_samples = []

# 应用所有过滤条件
for condition in filters:
    mask = filtered_df[condition["column"]].str.contains(condition["pattern"], regex=True, na=False)
    dropped_samples.append(filtered_df[mask])
    filtered_df = filtered_df[~mask]

# 保存为新的Excel文件
excel_filename = f"../data/filtered_mindspore_forum_data.xlsx"
filtered_df.to_excel(excel_filename, index=False)

print(f"原始数据条数: {len(df)}")
print(f"过滤后数据条数: {len(filtered_df)}")
print(f"过滤后的数据已保存至 {excel_filename}")
