# -*- coding: utf-8 -*-
"""
Optimized SRTM processor with lightweight GeoJSON and enhanced search
"""

import rasterio
import numpy as np
from haversine import haversine
import pandas as pd
import folium
from folium.plugins import FastMarkerCluster, Search
import json

# --------------------------------------
# 1. Load and Process SRTM Data
# --------------------------------------
tif_file = r"C:\Users\USERNAME\Downloads\Personal maps\elevation_data.gtiff"

with rasterio.open(tif_file) as src:
    elevation_data = src.read(1)
    transform = src.transform
    nodata = src.nodata

# Optimized numpy-based processing
valid_mask = (elevation_data >= 3700) & (elevation_data != nodata)
rows, cols = np.where(valid_mask)

# Vectorized coordinate conversion
coordinates = np.column_stack([cols, rows])
lons, lats = rasterio.transform.xy(transform, rows, cols)

# Now `lons` and `lats` are arrays with the correct coordinates
distances = np.array([haversine((4.7109, -74.0721), (lat, lon), unit='km')
                      for lat, lon in zip(lats, lons)])

# Create GeoJSON-like structure directly
features = [
    {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [lon, lat]
        },
        "properties": {
            "elevation": float(elev),
            "distance": float(dist),
            "type": "elevation_point"
        }
    }
    for lat, lon, elev, dist in zip(lats, lons, elevation_data[rows, cols], distances)
    if dist <= 60
]

# --------------------------------------
# 2. Create Optimized Map
# --------------------------------------
m = folium.Map(location=[4.7109, -74.0721], zoom_start=9, tiles="CartoDB positron")

# Add elevation data as lightweight GeoJSON
elevation_layer = folium.GeoJson(
    json.dumps({"type": "FeatureCollection", "features": features}),
    name="Elevation Points",
    marker=folium.CircleMarker(radius=2, color="#3186cc", fill=True),
    tooltip=folium.GeoJsonTooltip(fields=["elevation", "distance"],
                                  aliases=["Elevation (m):", "Distance (km):"]),
    control=False
).add_to(m)

# Add search by place name
m.get_root().html.add_child(folium.Element("""
<script>
function searchByPlaceName() {
    const place = prompt("Enter place name (e.g., mountain, park, etc.):");

    if (!place) {
        alert("Please enter a valid place name.");
        return;
    }

    // Query Overpass API for place names in the current map bounds
    const bounds = map.getBounds();
    const bbox = `${bounds.getSouth()},${bounds.getWest()},${bounds.getNorth()},${bounds.getEast()}`;
    const overpassQuery = `[out:json][timeout:30];
        node["name"]({{bbox}});
        way["name"]({{bbox}});
        relation["name"]({{bbox}});
        out center;`;

    fetch(`https://overpass-api.de/api/interpreter?data=${encodeURIComponent(overpassQuery)}`)
        .then(response => response.json())
        .then(data => {
            let found = false;
            data.elements.forEach(item => {
                if (item.tags.name && item.tags.name.toLowerCase().includes(place.toLowerCase())) {
                    const coords = item.center ? [item.center.lat, item.center.lon] : [item.lat, item.lon];
                    L.marker(coords)
                        .bindPopup(`<b>${item.tags.name}</b><br>${item.tags.tourism || item.tags.natural || ''}`)
                        .addTo(map)
                        .openPopup();
                    found = true;
                }
            });

            if (!found) {
                alert("No matching places found.");
            }
        });
}
</script>
"""))

# Add button for searching place names
m.get_root().html.add_child(folium.Element("""
<button onclick="searchByPlaceName()" style="position: absolute; top: 50px; left: 10px; z-index: 9999; padding: 10px; background-color: #3186cc; color: white; border: none; border-radius: 5px;">Search by Place Name</button>
"""))

# Add performance-optimized elements
FastMarkerCluster(
    data=[[feature["geometry"]["coordinates"][1],
           feature["geometry"]["coordinates"][0]]
          for feature in features],
    name="Elevation Clusters",
    disableClusteringAtZoom=14,
    showCoverageOnHover=False
).add_to(m)

# Add dynamic legend
legend_html = '''
<div style="position: fixed; 
            bottom: 50px; right: 50px; 
            width: 180px; padding: 10px;
            border: 2px solid grey; z-index: 9999;
            font-size: 14px; background: white;
            opacity: 0.85; border-radius: 5px;">
    <h4 style="margin-top:0">Map Legend</h4>
    <div><i class="fa fa-circle" style="color:#3186cc"></i> Elevation Points</div>
    <div><i class="fa fa-flag" style="color:red"></i> Bogotá Center</div>
    <div><i class="fa fa-search"></i> Search for:</div>
    <ul style="margin:5px 0; padding-left:20px">
        <li>Elevation (e.g., "3700")</li>
        <li>Place names</li>
        <li>Coordinates (e.g., "4.7109, -74.0721")</li>
    </ul>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Add layer control and save
folium.LayerControl().add_to(m)
m.save("optimized_elevation_map_with_place_search.html")
print("Map saved with dynamic features and search by place name")
