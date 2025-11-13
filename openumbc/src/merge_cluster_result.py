import pandas as pd

if __name__ == "__main__":
    origin_data = pd.read_excel('../data/merged_issue_forum_release_v2.xlsx', sheet_name="Sheet1")
    origin_data = origin_data.fillna('')
    topics_summary = {}
    topic_graph_info = []
    for index, row in origin_data.iterrows():
        if not row['topic']:
            continue
        if row['topic'] not in topics_summary:
            topics_summary[row['topic']] = []
        topics_summary[row['topic']].append(index)
    
    for topic, indices in topics_summary.items():
        topic_graph_info.append({
            "Topic": -1,
            "Count": len(indices),
            "topic node": indices,
            "summary": topic
        })
    
    new_topic_info = pd.read_excel('../data/topic_graph_info.xlsx', sheet_name="Sheet1")

    topic_info = pd.DataFrame(topic_graph_info)
    merged_df = pd.concat([topic_info, new_topic_info], ignore_index=True)

    merged_df.to_excel('../data/topic_graph_info_merged.xlsx', index=False, engine='openpyxl')
