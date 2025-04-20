import osmnx as ox

# Set configuration settings
ox.settings.use_cache = True
ox.settings.log_console = False

# Download the road network for Baghdad
G = ox.graph_from_place("Baghdad, Iraq", network_type="drive")

# Print basic stats about the graph
print(ox.basic_stats(G))

# # Save the graph to a file (optional)
ox.save_graphml(G, filepath="baghdad_road_network.graphml")
print("Road network saved to 'baghdad_road_network.graphml'")

# Load the graph if not already loaded
# G = ox.load_graphml(filepath="baghdad_road_network.graphml")

# Plot the road network
fig, ax = ox.plot_graph(G, node_size=0, edge_color="gray", bgcolor="white")