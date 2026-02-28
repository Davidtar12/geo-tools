import subprocess
import os


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


def process_files(paths, kml_file_path):
    supported_formats = [".png", ".jpg", ".jpeg", ".webp", ".raf"]
    files = []
    kml_entries = []
    for path in paths:
        if os.path.isdir(path):
            files.extend([os.path.join(path, f) for f in os.listdir(path) if
                          os.path.splitext(f.lower())[1] in supported_formats])
        elif os.path.isfile(path) and os.path.splitext(path.lower())[1] in supported_formats:
            files.append(path)

    # Extract GPS data from each file
    for file_path in files:
        latitude, longitude = extract_gps_data(file_path)
        if latitude and longitude:
            print(f"File: {file_path} - Latitude: {latitude}, Longitude: {longitude}")
            kml_entries.append(create_kml_entry(file_path, latitude, longitude))
        else:
            print(f"File: {file_path} - GPS data not found")

    # Write to KML file
    with open(kml_file_path, 'w') as kml_file:
        kml_file.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n')
        for entry in kml_entries:
            kml_file.write(entry)
        kml_file.write('</Document>\n</kml>\n')


def main():
    paths = [r"C:\Users\USERNAME\Downloads\Fotos2\paracoords"]
    kml_file_path = r"C:\Users\USERNAME\Downloads\Fotos2\coordinates.kml"
    process_files(paths, kml_file_path)


if __name__ == "__main__":
    main()
