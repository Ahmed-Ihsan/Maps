import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from math import radians, sin, cos, sqrt, atan2

# Define a custom great-circle distance heuristic for A*
def great_circle_heuristic(node1, node2):
    # Extract latitude and longitude of the nodes
    lat1, lon1 = G.nodes[node1]['y'], G.nodes[node1]['x']
    lat2, lon2 = G.nodes[node2]['y'], G.nodes[node2]['x']
    
    # Convert coordinates to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula to calculate great-circle distance
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return 6371000 * c  # Earth's radius in meters

# Load the graph from the saved GraphML file
G = ox.load_graphml(filepath="baghdad_road_network.graphml")

# Define the start and end points (latitude, longitude)
start_location = [33.3152, 44.3702]  # Near Baghdad Center
end_location = [33.4000, 44.4500]    # Another point in Baghdad

# Find the nearest nodes to the start and end locations
origin_node = ox.distance.nearest_nodes(G, start_location[1], start_location[0])
destination_node = ox.distance.nearest_nodes(G, end_location[1], end_location[0])

# Prompt the user to select an algorithm
print("Select a pathfinding algorithm:")
print("1. Dijkstra")
print("2. A*")
print("3. Bellman-Ford")
choice = input("Enter your choice (1/2/3): ")

if choice == "1":
    print("Calculating shortest path using Dijkstra...")
    route = nx.dijkstra_path(G, origin_node, destination_node, weight="length")
    route_color = "blue"
    route_label = "Dijkstra"
elif choice == "2":
    print("Calculating shortest path using A*...")
    route = nx.astar_path(G, origin_node, destination_node, heuristic=great_circle_heuristic, weight="length")
    route_color = "green"
    route_label = "A*"
elif choice == "3":
    print("Calculating shortest path using Bellman-Ford...")
    route = nx.bellman_ford_path(G, origin_node, destination_node, weight="length")
    route_color = "red"
    route_label = "Bellman-Ford"
else:
    print("Invalid choice. Defaulting to Dijkstra.")
    route = nx.dijkstra_path(G, origin_node, destination_node, weight="length")
    route_color = "blue"
    route_label = "Dijkstra"

# Plot the graph with the selected route highlighted
fig, ax = ox.plot_graph_route(
    G,
    route,
    route_color=route_color,
    route_linewidth=6,
    node_size=0,
    bgcolor="white",
    show=False,
    close=False
)

# Add markers for the start and end points
ax.scatter(
    start_location[1], start_location[0],
    c="purple", s=150, label="Start Point", zorder=2
)
ax.scatter(
    end_location[1], end_location[0],
    c="orange", s=150, label="End Point", zorder=2
)

# Add a legend
ax.legend(
    handles=[
        plt.Line2D([0], [0], color=route_color, lw=4, label=route_label),
        plt.Line2D([], [], marker='o', color='w', markerfacecolor='purple', markersize=10, label='Start Point'),
        plt.Line2D([], [], marker='o', color='w', markerfacecolor='orange', markersize=10, label='End Point')
    ],
    loc="upper right"
)

# Show the plot
plt.show()