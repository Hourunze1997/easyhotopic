import pandas as pd

def merge_excel_files(discuss_path, gitcode_path, output_path):
    # 读取讨论区数据
    discuss_df = pd.read_excel(discuss_path)[[
        'url', 'title', 'body', 'processed_body'
    ]]
    # 读取GitCode数据并转换字段
    gitcode_df = pd.read_excel(gitcode_path)
    gitcode_df = gitcode_df[['url', 'title', 'body', 'processed_body']]
    # 合并数据
    merged_df = pd.concat([discuss_df, gitcode_df], ignore_index=True)

    # 保存结果
    merged_df.to_excel(output_path, index=False)
    print(f"合并完成，结果已保存到: {output_path}")
  

if __name__ == "__main__":
    input_file = "../data/processed_forum_topics.xlsx"
    topic_info = "../data/processed_issues_new.xlsx"
    output_file = "../data/merged_issue_forum_new.xlsx"
    merge_excel_files(input_file, topic_info, output_file)
    print("merge data success")
