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


def process_files(paths):
    supported_formats = [".png", ".jpg", ".jpeg", ".webp", ".raf"]
    files = []
    for path in paths:
        if os.path.isdir(path):
            # Add all supported files in the directory to the list
            files.extend([os.path.join(path, f) for f in os.listdir(path) if
                          os.path.splitext(f.lower())[1] in supported_formats])
        elif os.path.isfile(path) and os.path.splitext(path.lower())[1] in supported_formats:
            # Add supported file to the list
            files.append(path)

    # Extract GPS data from each file
    for file_path in files:
        latitude, longitude = extract_gps_data(file_path)
        if latitude and longitude:
            print(f"File: {file_path} - Latitude: {latitude}, Longitude: {longitude}")
        else:
            print(f"File: {file_path} - GPS data not found")


def main():
    # Predefined paths: add paths to image files or directories containing image files here
    paths = [
        r"C:\Users\USERNAME\Downloads\FOTOS"
    ]
    process_files(paths)


if __name__ == "__main__":
    main()