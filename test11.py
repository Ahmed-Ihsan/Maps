import osmnx as ox
import networkx as nx
import folium
import json
import matplotlib.pyplot as plt
from math import radians, sin, cos, sqrt, atan2
from branca.element import MacroElement
from jinja2 import Template
import geopandas as gpd

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

# Load the graph with precomputed elevation data
G = ox.load_graphml(filepath="baghdad_road_network.graphml")

# Define the center of Baghdad
center_location = [33.3152, 44.3702]

# Create a Folium map centered at Baghdad
m = folium.Map(location=center_location, zoom_start=12, tiles=None)

# Add offline basemaps (pre-downloaded tiles)
folium.TileLayer(
    tiles="data/openstreetmap_tiles/{z}/{x}/{y}.png",  # Path to pre-downloaded OpenStreetMap tiles
    attr="OpenStreetMap",
    name="Offline OpenStreetMap",
    overlay=False,
    control=True
).add_to(m)

folium.TileLayer(
    tiles="data/satellite_tiles/{z}/{x}/{y}.png",  # Path to pre-downloaded satellite tiles
    attr="Esri World Imagery",
    name="Offline Satellite",
    overlay=False,
    control=True
).add_to(m)

# Add JavaScript to handle map clicks for start and end selection
js_click_handler = """
<script>
var selectedPoints = [];
var startMarker = null;
var endMarker = null;

function handleMapClick(e) {
    var latlng = e.latlng;
    var lat = latlng.lat;
    var lng = latlng.lng;

    // Remove previous markers if they exist
    if (startMarker !== null) {
        map.removeLayer(startMarker);
    }
    if (endMarker !== null) {
        map.removeLayer(endMarker);
    }

    // Add the clicked point to the list of selected points
    selectedPoints.push([lat, lng]);

    // Add a new marker for the clicked point
    if (selectedPoints.length === 1) {
        startMarker = L.marker([lat, lng], {icon: L.icon({iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x-green.png', iconSize: [25, 41], iconAnchor: [12, 41]})})
            .addTo(map)
            .bindPopup("Start Point")
            .openPopup();
        console.log("Start point set: Latitude=" + lat + ", Longitude=" + lng);
    } else if (selectedPoints.length === 2) {
        endMarker = L.marker([lat, lng], {icon: L.icon({iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x-red.png', iconSize: [25, 41], iconAnchor: [12, 41]})})
            .addTo(map)
            .bindPopup("End Point")
            .openPopup();
        console.log("End point set: Latitude=" + lat + ", Longitude=" + lng);

        // Send the selected points to Python via URL hash
        var urlHash = "#start=" + selectedPoints[0][0] + "," + selectedPoints[0][1] + "&end=" + selectedPoints[1][0] + "," + selectedPoints[1][1];
        window.location.hash = urlHash;

        // Reset the selection
        selectedPoints = [];
    }
}

// Attach the click event listener to the map
map.on('click', handleMapClick);
</script>
"""

# Save the map to an HTML file with the JavaScript click handler
output_file = "interactive_route_selection.html"
m.get_root().header.add_child(folium.Element(js_click_handler))

# Function to compute and display routes
def compute_and_display_routes(start_location, end_location):
    global G
    
    # Find the nearest nodes to the start and end locations
    origin_node = ox.distance.nearest_nodes(G, start_location[1], start_location[0])
    destination_node = ox.distance.nearest_nodes(G, end_location[1], end_location[0])
    
    # Function to find an alternative route by removing edges from the graph
    def find_alternative_route(G, origin_node, destination_node, excluded_edges, heuristic, weight="length"):
        G_copy = G.copy()
        for u, v, k in excluded_edges:
            if G_copy.has_edge(u, v, key=k):
                G_copy.remove_edge(u, v, key=k)
        try:
            route = nx.astar_path(G_copy, origin_node, destination_node, heuristic=heuristic, weight=weight)
            return route
        except nx.NetworkXNoPath:
            return None
    
    # Number of routes to generate
    num_routes = 3
    
    # Step 1: Find the primary A* route
    primary_route = nx.astar_path(G, origin_node, destination_node, heuristic=great_circle_heuristic, weight="length")
    routes = [primary_route]
    
    # Step 2: Find additional alternative routes
    excluded_edges = []
    for i in range(1, num_routes):
        route_edges = [(routes[-1][j], routes[-1][j + 1], 0) for j in range(len(routes[-1]) - 1)]
        excluded_edges.extend(route_edges)
        alternative_route = find_alternative_route(
            G, origin_node, destination_node, excluded_edges, heuristic=great_circle_heuristic, weight="length"
        )
        if alternative_route is not None and alternative_route not in routes:
            routes.append(alternative_route)
    
    # Ensure we have exactly `num_routes` routes
    if len(routes) < num_routes:
        while len(routes) < num_routes:
            routes.append(routes[0])
    
    # Assign unique colors for each route
    colors = ["blue", "green", "red"][:len(routes)]
    
    # Plot the routes on the map
    for i, route in enumerate(routes):
        route_coordinates = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]
        folium.PolyLine(
            locations=route_coordinates,
            color=colors[i],
            weight=5,
            opacity=0.8,
            popup=f"Route {i + 1}"
        ).add_to(m)
    
    # Add start and end markers
    folium.Marker(start_location, icon=folium.Icon(color="green"), popup="Start Point").add_to(m)
    folium.Marker(end_location, icon=folium.Icon(color="red"), popup="End Point").add_to(m)
    
    # Fit bounds to include all routes
    bounds = [
        (min(start_location[0], end_location[0]), min(start_location[1], end_location[1])),
        (max(start_location[0], end_location[0]), max(start_location[1], end_location[1]))
    ]
    m.fit_bounds(bounds)

    # Save the updated map
    m.save("map_with_routes.html")
    print("Routes computed and saved to 'map_with_routes.html'.")

# Function to save routes as GeoJSON
def save_routes_as_geojson(routes, output_file):
    features = []
    for i, route in enumerate(routes):
        coordinates = [(G.nodes[node]['x'], G.nodes[node]['y']) for node in route]
        feature = {
            "type": "Feature",
            "properties": {"route": f"Route {i + 1}"},
            "geometry": {
                "type": "LineString",
                "coordinates": coordinates
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    with open(output_file, "w") as f:
        json.dump(geojson, f)
    
    print(f"Routes saved as GeoJSON: {output_file}")

# Function to plot elevation profile
def plot_elevation_profile(route):
    elevations = [G.nodes[node].get('elevation', 0) for node in route]
    distances = [0]
    for i in range(1, len(route)):
        u, v = route[i - 1], route[i]
        edge_data = G.get_edge_data(u, v)[0]
        distances.append(distances[-1] + edge_data['length'])
    
    plt.figure(figsize=(10, 4))
    plt.plot(distances, elevations, marker='o', color='blue')
    plt.title("Elevation Profile")
    plt.xlabel("Distance (meters)")
    plt.ylabel("Elevation (meters)")
    plt.grid(True)
    plt.savefig("elevation_profile.png", dpi=300, bbox_inches="tight")
    print("Elevation profile saved as 'elevation_profile.png'.")

# Function to calculate distance and time for a route
def calculate_route_stats(route, speed_kph=50):  # Default speed: 50 km/h
    total_distance = sum(G[u][v][0]['length'] for u, v in zip(route[:-1], route[1:]))
    total_time = total_distance / (speed_kph * 1000 / 3600)  # Convert to hours
    return total_distance, total_time

# Function to generate turn-by-turn directions
def get_turn_by_turn_directions(route):
    directions = []
    for u, v in zip(route[:-1], route[1:]):
        edge_data = G.get_edge_data(u, v)[0]
        directions.append(edge_data.get("name", "Unnamed Road"))
    return directions

# Function to add precomputed POIs to the map
def add_pois_to_map():
    # Load precomputed POIs from a GeoJSON file
    pois = gpd.read_file("baghdad_pois.geojson")
    
    # Add POIs as markers on the map
    for _, row in pois.iterrows():
        if hasattr(row["geometry"], "y") and hasattr(row["geometry"], "x"):  # Ensure geometry has coordinates
            folium.Marker(
                location=[row["geometry"].y, row["geometry"].x],
                popup=row["name"] if "name" in row else "Unknown POI",
                icon=folium.Icon(color="orange", icon="info-sign")
            ).add_to(m)

    print("Precomputed points of interest added to the map.")

# Function to add terrain information
def add_terrain_information():
    for u, v, data in G.edges(data=True):
        grade = data.get("grade_abs", 0)
        color = "green" if grade < 0.05 else ("yellow" if grade < 0.1 else "red")
        folium.PolyLine(
            locations=[(G.nodes[u]['y'], G.nodes[u]['x']), (G.nodes[v]['y'], G.nodes[v]['x'])],
            color=color,
            weight=2,
            opacity=0.8
        ).add_to(m)

# Function to add a search bar for preloaded locations
def add_search_bar():
    search_data = [
        {"name": "Baghdad Center", "location": [33.3152, 44.3702]},
        {"name": "Al-Mustansiriya University", "location": [33.3214, 44.3954]},
        {"name": "Zawra'a Park", "location": [33.3122, 44.3978]}
    ]

    template = """
    {% macro html(this, kwargs) %}
    <div style="position: fixed; top: 10px; right: 10px; z-index: 1000; background: white; padding: 10px; border: 1px solid #ccc;">
        <select onchange="handleSearch(this.value)">
            <option value="">-- Select Location --</option>
            {% for item in this.search_data %}
            <option value="{{item.location[0]}},{{item.location[1]}}">{{item.name}}</option>
            {% endfor %}
        </select>
    </div>
    <script>
    function handleSearch(coords) {
        if (!coords) return;
        var latlng = coords.split(",");
        map.flyTo([latlng[0], latlng[1]], 16);
    }
    </script>
    {% endmacro %}
    """

    macro = MacroElement()
    macro._template = Template(template)
    macro.search_data = search_data
    m.get_root().add_child(macro)

# Add measurement tool
from folium.plugins import MeasureControl
MeasureControl(position="topleft", primary_length_unit="kilometers").add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Add precomputed POIs to the map
# add_pois_to_map()

# Add terrain information
add_terrain_information()

# Add search bar
add_search_bar()

# Save the initial map
m.save("offline_map.html")
print("Initial map saved to 'offline_map.html'. Open it in your browser.")