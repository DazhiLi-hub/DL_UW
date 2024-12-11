import networkx as nx

#20 ， 1000， 3000
# Create a graph with 1000 vertices and 2000 edges
G = nx.gnm_random_graph(3000, 18000)

# Add an articulation point by making a bridge
G.add_edge(1500, 1501)

# Find articulation points
articulation_points = list(nx.articulation_points(G))

num_answer = len(articulation_points)

if num_answer:
    with open("graph3000a.txt", "w") as file:
        file.write("num articulation point is " + str(num_answer) + "\n")
        edges = list(G.edges())
        for edge in edges:
            file.write(f"{edge[0]} {edge[1]}\n")
    file.close()
else:
    print("No articulation point")