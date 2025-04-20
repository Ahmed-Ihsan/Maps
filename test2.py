import folium
from folium.plugins import MeasureControl
import osmnx as ox
import networkx as nx

# Set configuration settings manually for older versions of osmnx
ox.settings.use_cache = True
ox.settings.log_console = True

# Define the center of Iraq
iraq_center = [33.2232, 43.6786]  # Approximate center of Iraq

# Download the road network for Iraq
G = ox.graph_from_place("Iraq", network_type="drive")  # "drive" includes roads suitable for vehicles

# Convert the graph to a format compatible with Folium
gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)

# Create a Folium map centered at Iraq
m = folium.Map(location=iraq_center, zoom_start=6, tiles=None)

# Add multiple tile layers (base maps)
folium.TileLayer(
    tiles='OpenStreetMap',
    attr='OpenStreetMap',
    name='OpenStreetMap',
    overlay=False,
    control=True
).add_to(m)

folium.TileLayer(
    tiles='Stamen Terrain',
    attr='Stamen',
    name='Terrain Map',
    overlay=False,
    control=True
).add_to(m)

folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri World Imagery',
    name='Satellite Map',
    overlay=False,
    control=True
).add_to(m)

# Add markers for major cities in Iraq
cities = [
    {"name": "Baghdad", "location": [33.3152, 44.3702], "info": "Capital of Iraq"},
    {"name": "Basra", "location": [30.5139, 47.7964], "info": "Major port city in southern Iraq"},
    {"name": "Mosul", "location": [36.3354, 43.1194], "info": "Second-largest city in Iraq"},
    {"name": "Erbil", "location": [36.1944, 44.0006], "info": "Capital of Iraqi Kurdistan"},
    {"name": "Kirkuk", "location": [35.4900, 44.3900], "info": "Oil-rich city in northern Iraq"},
]

for city in cities:
    folium.Marker(
        location=city["location"],
        popup=f"<strong>{city['name']}</strong><br>{city['info']}",
        tooltip=city["name"]
    ).add_to(m)

# Find the nearest nodes in the graph for the start and end points
start_location = [33.3152, 44.3702]  # Baghdad
end_location = [30.5139, 47.7964]   # Basra

origin_node = ox.distance.nearest_nodes(G, start_location[1], start_location[0])
destination_node = ox.distance.nearest_nodes(G, end_location[1], end_location[0])

# Calculate the shortest path using A* (based on travel time or distance)
route = nx.shortest_path(G, origin_node, destination_node, weight="length")  # "length" uses road distances

# Extract the coordinates of the route
route_coordinates = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]

# Add the route to the map
folium.PolyLine(
    locations=route_coordinates,
    color='blue',
    weight=5,
    opacity=0.7,
    popup="Shortest Path from Baghdad to Basra"
).add_to(m)

# Add layer control to switch between base maps
folium.LayerControl().add_to(m)

# Add a measure control tool for distance measurement
MeasureControl(position='topleft', primary_length_unit='kilometers').add_to(m)

# Fit the map to Iraq's bounding box
iraq_bounds = [[29.0, 38.0], [38.0, 49.0]]  # Approximate bounds of Iraq
m.fit_bounds(iraq_bounds)

# Save the map to an HTML file
output_file = "professional_map_of_iraq_with_route.html"
m.save(output_file)
print(f"Professional map of Iraq with shortest path saved to {output_file}")