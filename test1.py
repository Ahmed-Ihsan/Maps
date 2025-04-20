import folium

# Create a map centered at a specific location (latitude, longitude)
m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

# Add a predefined tile layer (e.g., Stamen Terrain)
folium.TileLayer(
    tiles='Stamen Terrain',
    attr='Stamen',
    name='Terrain Map',
    overlay=False,
    control=True
).add_to(m)

# Save the map to an HTML file
output_file = "offline_map.html"
m.save(output_file)

print(f"Map saved to {output_file}")