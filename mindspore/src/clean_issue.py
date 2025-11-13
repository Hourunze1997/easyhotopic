import pandas as pd

def filter_data(df):
    pattern = r'开源实习|测试任务|任务'
    return df[~df['title'].str.contains(pattern, regex=True, na=False)]

# 读取Excel文件
input_file = "../data/mindspore_issue_data.xlsx"
df = pd.read_excel(input_file)

# 过滤数据
filtered_df = filter_data(df)

# 保存为新的Excel文件
excel_filename = f"../data/filtered_mindspore_issue_data.xlsx"
filtered_df.to_excel(excel_filename, index=False)

print(f"原始数据条数: {len(df)}")
print(f"过滤后数据条数: {len(filtered_df)}")
print(f"过滤后的数据已保存至 {excel_filename}")
