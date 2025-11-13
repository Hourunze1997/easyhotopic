import networkx as nx
import pandas as pd
import numpy as np

def get_connected_graphs(nodes):
    # 创建不连通的图
    G = nx.Graph()
    G.add_edges_from(nodes)

    # 获取所有连通分量
    components = list(nx.connected_components(G))

    # 生成子图列表
    subgraphs = [G.subgraph(c).copy() for c in components]

    # 输出每个子图的节点
    count = 0
    max_len = 0
    topic_graph = []
    # 使用sorted函数生成新排序列表
    for i, sg in enumerate(subgraphs):
        max_len = max(max_len, len(sg.nodes()))
        # print(f"子图 {i+1} 的节点:", sg.nodes())
        topic_graph.append(list(sg.nodes()))
        if len(sg.nodes()) > 5:
            count += 1
    print(f"总共有 {len(subgraphs)} 个子图, 其中大于5个节点的子图有 {count} 个, 最大的子图有 {max_len} 个节点")
    sorted_arr = sorted(topic_graph, key=lambda x: len(x), reverse=True)
    # for i, arr in enumerate(sorted_arr):
    #     print(f"子图 {i+1} 的子图:", arr)
    return sorted_arr

if __name__ == "__main__":
    edges = []
    nodes = []
    df = pd.read_excel('../data/graph_nodes.xlsx', sheet_name="Sheet1")
    for _, row in df.iterrows():
        in_id = row['in_id']
        out_id = row['out_id']
        edges.append((in_id, out_id))
        nodes.append(in_id)
        nodes.append(out_id)
    # nodes = [(1, 2), (2, 3), (4, 5), (5, 6), (7, 8)]
    print(f"nodes length: {len(set(nodes))}")
    topic_graph = get_connected_graphs(edges)
    topic_graph_info = []
    origin_df = pd.read_excel('../data/merged_issue_forum_new.xlsx', sheet_name="Sheet1")
    tmp_index = {}
    for i, topic in enumerate(topic_graph):
        topic_graph_info.append({
            "Topic": i,
            "Count": len(topic),
            "topic node": topic
        })
        for node in topic:
            tmp_index[node] = i
    topic_info = pd.DataFrame(topic_graph_info)
    topic_info.to_excel('../data/topic_graph_info.xlsx', index=False, engine='openpyxl')
    topic = []
    for i, row in origin_df.iterrows():
        res = tmp_index.get(i, -1)
        topic.append(res)
    origin_df['Topic'] = topic
    origin_df.to_excel('../data/topic_graph_doc.xlsx', index=False, engine='openpyxl')
