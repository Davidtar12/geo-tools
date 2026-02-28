import subprocess
import os
from collections import defaultdict

def extract_gps_data(file_path):
    # Command to get GPS data using exiftool
    exiftool_path = r"C:\Users\USERNAME\Downloads\exiftool-12.84\exiftool.exe"
    command = [exiftool_path, '-GPSLatitude', '-GPSLongitude', '-n', file_path]
    process = subprocess.run(command, stdout=subprocess.PIPE, text=True)
    output = process.stdout
    # Parse the output for coordinates
    latitude = longitude = None
    for line in output.split('\n'):
        if 'GPS Latitude' in line:
            latitude = line.split(':')[-1].strip()
        elif 'GPS Longitude' in line:
            longitude = line.split(':')[-1].strip()
    return latitude, longitude

def create_kml_entry(file_path, latitude, longitude):
    return f"""
<Placemark>
<name>{os.path.basename(file_path)}</name>
<Point>
<coordinates>{longitude},{latitude},0</coordinates>
</Point>
</Placemark>
"""

def process_files(paths, kml_file_path, output_folder):
    supported_formats = [".png", ".jpg", ".jpeg", ".webp", ".raf"]
    files = []
    kml_entries = []
    coordinate_groups = defaultdict(list)

    for path in paths:
        if os.path.isdir(path):
            files.extend([os.path.join(path, f) for f in os.listdir(path) if os.path.splitext(f.lower())[1] in supported_formats])
        elif os.path.isfile(path) and os.path.splitext(path.lower())[1] in supported_formats:
            files.append(path)

    # Extract GPS data from each file and group by coordinates
    for file_path in files:
        latitude, longitude = extract_gps_data(file_path)
        if latitude and longitude:
            print(f"File: {file_path} - Latitude: {latitude}, Longitude: {longitude}")
            kml_entries.append(create_kml_entry(file_path, latitude, longitude))
            coordinate_groups[(latitude, longitude)].append(file_path)
        else:
            print(f"File: {file_path} - GPS data not found")

    # Create subfolders and move files based on coordinates
    for coords, file_paths in coordinate_groups.items():
        lat, lon = coords
        subfolder = os.path.join(output_folder, f"lat_{lat}_lon_{lon}")
        os.makedirs(subfolder, exist_ok=True)
        for file_path in file_paths:
            new_path = os.path.join(subfolder, os.path.basename(file_path))
            os.rename(file_path, new_path)

    # Write to KML file
    with open(kml_file_path, 'w') as kml_file:
        kml_file.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n')
        for entry in kml_entries:
            kml_file.write(entry)
        kml_file.write('</Document>\n</kml>\n')

def main():
    paths = [r"C:\Users\USERNAME\Downloads\Fotos2\Fotos3"]
    kml_file_path = r"C:\Users\USERNAME\Downloads\Fotos2\coordinates2.kml"
    output_folder = r"C:\Users\USERNAME\Downloads\Fotos2\sorted_photos"
    process_files(paths, kml_file_path, output_folder)

if __name__ == "__main__":
    main()