import folium
from folium.plugins import MeasureControl, AntPath

# Define the center of Iraq
iraq_center = [33.2232, 43.6786]  # Approximate center of Iraq

# Create a map centered at Iraq
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

# Add layer control to switch between base maps
folium.LayerControl().add_to(m)

# Add a measure control tool for distance measurement
MeasureControl(position='topleft', primary_length_unit='kilometers').add_to(m)

# Add a short path between Baghdad and Basra
baghdad = [33.3152, 44.3702]  # Coordinates of Baghdad
basra = [30.5139, 47.7964]   # Coordinates of Basra

# Use AntPath for an animated path effect
AntPath(
    locations=[baghdad, basra],
    color='blue',
    weight=3,
    delay=1000,  # Animation speed in milliseconds
    popup="Short Path from Baghdad to Basra"
).add_to(m)

# Alternatively, use PolyLine for a static path
# folium.PolyLine(
#     locations=[baghdad, basra],
#     color='red',
#     weight=3,
#     opacity=0.8,
#     popup="Short Path from Baghdad to Basra"
# ).add_to(m)

# Fit the map to Iraq's bounding box
iraq_bounds = [[29.0, 38.0], [38.0, 49.0]]  # Approximate bounds of Iraq
m.fit_bounds(iraq_bounds)

# Save the map to an HTML file
output_file = "professional_map_of_iraq.html"
m.save(output_file)
print(f"Professional map of Iraq saved to {output_file}")