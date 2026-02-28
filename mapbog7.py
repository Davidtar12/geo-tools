import rasterio
import numpy as np
from haversine import haversine_vector, Unit
import folium
from folium.plugins import HeatMap
import json

# --------------------------------
# 1. Optimized Data Processing
# --------------------------------
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

# Downsampled data processing
mask = (elevation >= 3700) & (elevation != nodata)
y, x = np.where(mask)
y = y[::STEP]
x = x[::STEP]

lons, lats = rasterio.transform.xy(transform, x, y)
coords = np.column_stack([lats, lons])

distances = haversine_vector([BOGOTA_CENTER],
                             coords,
                             unit=Unit.KILOMETERS,
                             comb=True).ravel()

valid = distances <= SEARCH_RADIUS_KM
hyper_data = np.column_stack([
    coords[valid, 0],  # latitude
    coords[valid, 1],  # longitude
    elevation[y[valid], x[valid]]
])

print(f"Processed {len(hyper_data)} points (downsampled 1:{STEP})")

# --------------------------------
# 2. Lightweight Map
# --------------------------------
m = folium.Map(
    location=BOGOTA_CENTER,
    zoom_start=8,
    tiles="CartoDB dark_matter",
    control_scale=True,
    prefer_canvas=True  # Better performance
)

if len(hyper_data) > 0:
    HeatMap(
        data=[[lat, lon, elev / 1000] for lat, lon, elev in hyper_data],
        gradient={'0.3': 'blue', '0.5': 'cyan', '0.7': 'lime', '1.0': 'red'},
        radius=10,  # Reduced for performance
        blur=15,  # Reduced for performance
        min_opacity=0.5
    ).add_to(m)

# --------------------------------
# 3. Robust Search System
# --------------------------------
search_js = f"""
<script>
document.addEventListener('DOMContentLoaded', function() {{
    const hyperData = {json.dumps(hyper_data.tolist())};
    const map = {m.get_name()};
    let currentMarkers = null;

    // Search control UI
    const searchControl = L.control({{position: 'topright'}});
    searchControl.onAdd = function(map) {{
        const div = L.DomUtil.create('div', 'search-panel');
        div.innerHTML = `
            <div style="background:#1a1a1a;padding:15px;border-radius:8px;box-shadow:0 0 15px rgba(0,0,0,0.5);width:320px">
                <h4 style="color:#fff;margin:0 0 15px 0">Bogotá Region Search</h4>
                <input id="searchInput" placeholder="Enter place or coordinates" 
                       style="width:100%;padding:10px;margin-bottom:10px;background:#333;color:#fff;border:1px solid #444">
                <button onclick="executeSearch()" 
                        style="width:100%;padding:12px;background:#2196F3;color:#fff;border:none;border-radius:4px;cursor:pointer">
                    🔍 Search
                </button>
                <div style="margin-top:10px;color:#888;font-size:0.9em">
                    Examples: "4.71, -74.07" or "Chía"
                </div>
            </div>
        `;
        return div;
    }};
    searchControl.addTo(map);

    // Unified search function
    window.executeSearch = async function() {{
        const input = document.getElementById('searchInput').value.trim();
        if(!input) return alert('Please enter a search term');

        try {{
            let lat, lng;

            // Coordinate parsing with validation
            if(input.match(/^[-+]?([1-8]?\\d(\\.\\d+)?|90(\\.0+)?),\\s*[-+]?(180(\\.0+)?|((1[0-7]\\d)|([1-9]?\\d))(\\.\\d+)?$/)) {{
                const parts = input.split(',').map(p => parseFloat(p.trim()));
                [lat, lng] = parts;
                if(isNaN(lat) || isNaN(lng)) throw new Error('Invalid coordinates');
            }} 
            else {{
                // Geocode place name
                const response = await fetch(
                    `https://nominatim.openstreetmap.org/search?q=${{encodeURIComponent(input)}}&format=json&limit=1`
                );
                const results = await response.json();
                if(!results.length) throw new Error('Location not found');
                lat = parseFloat(results[0].lat);
                lng = parseFloat(results[0].lon);
            }}

            // Verify within 200km radius
            const distance = haversineDistance([{BOGOTA_CENTER[0]}, {BOGOTA_CENTER[1]}], [lat, lng]);
            if(distance > 200) throw new Error('Location outside 200km radius from Bogotá');

            showResults(lat, lng);

        }} catch (error) {{
            alert(error.message);
            console.error('Search error:', error);
        }}
    }};

    function showResults(lat, lng) {{
        // Clear previous results
        if(currentMarkers) {{
            map.removeLayer(currentMarkers);
            currentMarkers = null;
        }}

        currentMarkers = L.featureGroup().addTo(map);

        // Add search marker
        L.marker([lat, lng], {{
            icon: L.icon({{
                iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
                iconSize: [25, 41]
            }})
        }})
        .bindPopup(`Search Center<br>${{lat.toFixed(4)}}, ${{lng.toFixed(4)}}`)
        .addTo(currentMarkers);

        // Find nearby points within 20km
        let foundPoints = false;
        hyperData.forEach(([dlat, dlng, elev]) => {{
            if(haversineDistance([dlat, dlng], [lat, lng]) < 20) {{
                foundPoints = true;
                L.circleMarker([dlat, dlng], {{
                    radius: 5,
                    color: '#ff0000',
                    fillColor: '#ffaaaa',
                    fillOpacity: 0.7
                }})
                .bindPopup(`Elevation: ${{elev}}m`)
                .addTo(currentMarkers);
            }}
        }});

        // Handle results
        if(currentMarkers.getLayers().length > 0) {{
            map.fitBounds(currentMarkers.getBounds());
        }} else {{
            map.setView([lat, lng], 12);
            alert('No high elevation points found nearby');
        }}
    }}

    function haversineDistance(coord1, coord2) {{
        const R = 6371;
        const dLat = (coord2[0] - coord1[0]) * Math.PI/180;
        const dLon = (coord2[1] - coord1[1]) * Math.PI/180;
        const a = 
            Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(coord1[0] * Math.PI/180) * 
            Math.cos(coord2[0] * Math.PI/180) *
            Math.sin(dLon/2) * Math.sin(dLon/2);
        return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    }};
}});
</script>

<style>
.leaflet-top.leaflet-right {{
    margin-top: 70px;
    margin-right: 10px;
}}
.search-panel {{
    z-index: 1000;
    box-shadow: 0 2px 10px rgba(0,0,0,0.4);
}}
</style>
"""



m.get_root().html.add_child(folium.Element(search_js))

# --------------------------------
# 4. Generate Map
# --------------------------------
m.save("optimized_bogota_search.html")
print(f"Map generated successfully! Final size estimate: {len(hyper_data) // 1000}kB")