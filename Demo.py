import networkx as nx
import matplotlib.pyplot as plt
import random
import math

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号

def generate_topology_map(num_nodes=20, max_degree=5):
    # 1. 生成随机几何图 (带有物理 x,y 坐标)
    # 半径设定决定了连通性，模拟你想要的无死角和度数限制
    G = nx.random_geometric_graph(num_nodes, radius=0.4)

    # 移除度数过高的边，强行限制最高度数 (对应你蓝图中的 2.2)
    for node in list(G.nodes()):
        while G.degree(node) > max_degree:
            neighbors = list(G.neighbors(node))
            G.remove_edge(node, random.choice(neighbors))

    # 2. 计算权重：视觉物理距离 + 随机波动
    for u, v in G.edges():
        x1, y1 = G.nodes[u]['pos']
        x2, y2 = G.nodes[v]['pos']
        # 计算物理欧几里得距离
        euclidean_dist = math.hypot(x2 - x1, y2 - y1)

        # 加入 0.8 到 1.2 倍的随机波动，保证和视觉成比例但不绝对
        noise = random.uniform(0.8, 1.2)
        weight = round(euclidean_dist * noise, 2)

        # 将权重赋予边
        G.edges[u, v]['weight'] = weight

    return G


def plot_and_find_weakness(G, home_base, default_unit):
    pos = nx.get_node_attributes(G, 'pos')

    # 画底图
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightgray', node_size=500, font_weight='bold')

    # 标记权重
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

    # 标记实体
    nx.draw_networkx_nodes(G, pos, nodelist=[home_base], node_color='blue', node_size=800, label="Home Base")
    nx.draw_networkx_nodes(G, pos, nodelist=[default_unit], node_color='green', node_size=600, label="Default Unit")

    try:
        # 3. 核心机制：Dijkstra 寻找最短路径
        shortest_path = nx.dijkstra_path(G, source=default_unit, target=home_base, weight='weight')

        # 最短路径上的首个相邻节点即为“命门”
        achilles_heel = shortest_path[1] if len(shortest_path) > 1 else None

        if achilles_heel is not None:
            nx.draw_networkx_nodes(G, pos, nodelist=[achilles_heel], node_color='red', node_size=700,
                                   label="Achilles' Heel (命门)")

            # 高亮显示最短路径的连线
            path_edges = list(zip(shortest_path, shortest_path[1:]))
            nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2.5)
            print(f"-> 默认单位在节点 {default_unit}，大本营在 {home_base}。")
            print(f"-> Dijkstra 最短路径为: {shortest_path}")
            print(f"-> 暴露的命门节点是: {achilles_heel}")

    except nx.NetworkXNoPath:
        print("警告：图不连通，没有路径！")

    plt.legend()
    plt.title("Topological Gambit Prototype")
    plt.show()


# 运行测试
if __name__ == "__main__":
    game_map = generate_topology_map(num_nodes=15, max_degree=5)

    # 假设你把大本营放在节点 0，把默认单位拍在节点 5
    # 你可以每次更改这两个数字，重新运行，来体验“命门”是怎么被算出来的
    plot_and_find_weakness(game_map, home_base=0, default_unit=5)