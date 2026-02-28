import rasterio
import numpy as np
from haversine import haversine_vector, Unit
import folium
from folium.plugins import HeatMap, Geocoder

# -------------------------------
# 1. Optimized Data Processing
# -------------------------------
TIF_FILE = r"C:\Users\USERNAME\Downloads\Personal maps\elevation_data.gtiff"
BOGOTA_CENTER = [4.7109, -74.0721]
SEARCH_RADIUS_KM = 200
STEP = 50  # Downsampling factor

with rasterio.open(TIF_FILE) as src:
    if src.crs != "EPSG:4326":
        raise ValueError("Requires WGS84 (EPSG:4326) coordinate system")
    elevation = src.read(1)
    transform = src.transform
    nodata = src.nodata or -32768.0

# Create a mask for elevation values above 3700m (excluding nodata)
mask = (elevation >= 3700) & (elevation != nodata)
y, x = np.where(mask)
y = y[::STEP]
x = x[::STEP]

# Convert row, column indices to geographic coordinates (lat, lon)
lons, lats = rasterio.transform.xy(transform, x, y)
coords = np.column_stack([lats, lons])

# Compute distances from the Bogotá center and filter points within SEARCH_RADIUS_KM
distances = haversine_vector([BOGOTA_CENTER], coords, unit=Unit.KILOMETERS, comb=True).ravel()
valid = distances <= SEARCH_RADIUS_KM

# Create the final data array: [latitude, longitude, elevation]
hyper_data = np.column_stack([
    coords[valid, 0],  # latitude
    coords[valid, 1],  # longitude
    elevation[y[valid], x[valid]]
])
print(f"Processed {len(hyper_data)} points (downsampled 1:{STEP})")

# -------------------------------
# 2. Create the Folium Map & HeatMap
# -------------------------------
m = folium.Map(
    location=BOGOTA_CENTER,
    zoom_start=8,
    tiles="CartoDB dark_matter",
    control_scale=True,
    prefer_canvas=True
)

if len(hyper_data) > 0:
    # Scale elevation (in meters) for display (dividing by 1000 to convert to km, for instance)
    HeatMap(
        data=[[lat, lon, elev / 1000] for lat, lon, elev in hyper_data],
        gradient={'0.3': 'blue', '0.5': 'cyan', '0.7': 'lime', '1.0': 'red'},
        radius=10,
        blur=15,
        min_opacity=0.5
    ).add_to(m)

# -------------------------------
# 3. Add the Geocoder Search Control
# -------------------------------
# This adds an interactive search bar (at the top left) that lets users enter a location.
# When a match is found, a marker is placed and the map zooms in (to zoom level 12).
geocoder = Geocoder(collapsed=False, position="topleft", add_marker=True, zoom=12)
geocoder.add_to(m)

# -------------------------------
# 4. Save the Map
# -------------------------------
output_filename = "optimized_bogota_search_with_geocoder.html"
m.save(output_filename)
print(f"Map generated successfully: {output_filename}")
