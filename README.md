# geo-tools

Geospatial Python: GPS EXIF extractor from photos, KML/shapefile generator, interactive maps.

## Scripts

| Script | Description |
|--------|-------------|
| `wk-img-coord-extractor.py` | Extract GPS latitude/longitude from photo EXIF metadata and output as CSV |
| `wk-img-coords-into-kml-shapefile.py` | Convert GPS coordinates from photos into KML (Google Earth) and shapefile (QGIS/ArcGIS) |
| `wk-coords-by-folder-fotos.py` | Batch process all photos in a folder — extract coordinates and create a location map |
| `mountains-bogota.py` / `mapbog7.py` | Interactive elevation and topographic map of Bogotá mountains using Folium |
| `wk-map.py` | General-purpose interactive map generator from a CSV of coordinates |

## Prerequisites

- Python 3.9+
- Photos with embedded GPS EXIF data (most modern smartphones)
- Optional: QGIS or Google Earth for viewing KML/shapefile output

## Setup

```bash
pip install -r requirements.txt
```

No API key required.

## Usage

```bash
# Extract GPS from all photos in a folder
python wk-coords-by-folder-fotos.py --folder /path/to/photos

# Generate KML for Google Earth
python wk-img-coords-into-kml-shapefile.py --input coords.csv --output locations.kml

# Interactive Bogotá map (opens in browser)
python mountains-bogota.py
```

## Notes

- Output KML files open directly in Google Earth and Google Maps (import).
- Shapefiles are compatible with QGIS, ArcGIS, and any GIS software.
- Photos without GPS data are skipped with a warning.

## Built with

Python · Folium · Pillow (EXIF) · shapefile  
AI-assisted development (Claude, GitHub Copilot) — architecture, requirements, QA validation and debugging by me.
