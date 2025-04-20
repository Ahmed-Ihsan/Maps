import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

# Load the graph from the saved GraphML file
G = ox.load_graphml(filepath="baghdad_road_network.graphml")

# Define the start and end points (latitude, longitude)
start_location = [33.3152, 44.3702]  # Near Baghdad Center
end_location = [33.4000, 44.4500]    # Another point in Baghdad

# Find the nearest nodes to the start and end locations
origin_node = ox.distance.nearest_nodes(G, start_location[1], start_location[0])
destination_node = ox.distance.nearest_nodes(G, end_location[1], end_location[0])

# Calculate the shortest path using NetworkX (based on road length)
route = nx.shortest_path(G, origin_node, destination_node, weight="length")

# Plot the graph with the shortest path highlighted
fig, ax = ox.plot_graph_route(
    G,
    route,
    route_color="red",
    route_linewidth=6,
    node_size=0,
    bgcolor="white",
    show=True,
    close=False
)

# Add markers for the start and end points
ax.scatter(
    start_location[1], start_location[0],
    c="green", s=100, label="Start Point", zorder=2
)
ax.scatter(
    end_location[1], end_location[0],
    c="blue", s=100, label="End Point", zorder=2
)

# Add a legend
ax.legend()

# Show the plot
plt.show()