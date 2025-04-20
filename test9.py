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

# Function to find an alternative route by removing edges from the graph
def find_alternative_route(G, origin_node, destination_node, excluded_edges, heuristic, weight="length"):
    # Create a copy of the graph to avoid modifying the original
    G_copy = G.copy()
    
    # Remove the excluded edges from the copied graph
    for u, v, k in excluded_edges:
        if G_copy.has_edge(u, v, key=k):
            G_copy.remove_edge(u, v, key=k)
    
    try:
        # Compute the A* route on the modified graph
        route = nx.astar_path(G_copy, origin_node, destination_node, heuristic=heuristic, weight=weight)
        return route
    except nx.NetworkXNoPath:
        # If no path exists, return None
        return None

# Number of routes to generate
num_routes = 5  # Change this value to generate more or fewer routes

# Step 1: Find the primary A* route
primary_route = nx.astar_path(G, origin_node, destination_node, heuristic=great_circle_heuristic, weight="length")
routes = [primary_route]

# Step 2: Find additional alternative routes
excluded_edges = []

for i in range(1, num_routes):
    # Get the edges of the last computed route
    route_edges = [(routes[-1][j], routes[-1][j + 1], 0) for j in range(len(routes[-1]) - 1)]
    
    # Add these edges to the excluded list
    excluded_edges.extend(route_edges)
    
    # Find an alternative route by excluding the previously used edges
    alternative_route = find_alternative_route(
        G, origin_node, destination_node, excluded_edges, heuristic=great_circle_heuristic, weight="length"
    )
    
    if alternative_route is not None and alternative_route not in routes:
        routes.append(alternative_route)
        print(f"Found alternative route {i}.")
    else:
        print(f"Could not find alternative route {i}. Reusing previous routes.")
        break

# Ensure we have exactly `num_routes` routes
if len(routes) < num_routes:
    print(f"Not enough distinct routes found. Reusing the primary route.")
    while len(routes) < num_routes:
        routes.append(routes[0])

# Assign unique colors for each route
colors = ["blue", "green", "red", "purple", "orange", "brown", "pink", "gray", "cyan", "magenta"][:len(routes)]

# Plot the graph with all routes highlighted
fig, ax = ox.plot_graph_routes(
    G,
    routes,
    route_colors=colors,
    route_linewidths=[4] * len(routes),
    node_size=0,
    bgcolor="white",
    show=False,
    close=False
)

# Add markers for the start and end points
ax.scatter(
    start_location[1], start_location[0],
    c="black", s=150, label="Start Point", zorder=2
)
ax.scatter(
    end_location[1], end_location[0],
    c="black", s=150, label="End Point", zorder=2
)

# Add a legend for the routes
legend_handles = [
    plt.Line2D([0], [0], color=color, lw=4, label=f"Route {i + 1}")
    for i, color in enumerate(colors)
]
legend_handles.extend([
    plt.Line2D([], [], marker='o', color='w', markerfacecolor='black', markersize=10, label='Start/End Point')
])

ax.legend(handles=legend_handles, loc="upper right")

# Show the plot
plt.show()