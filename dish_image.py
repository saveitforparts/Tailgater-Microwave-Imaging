import numpy as np
import matplotlib.pyplot as plt
import sys

# Function to load data from a file


def load_data(file_name):
    with open(file_name, 'r') as f:
        return np.loadtxt(f)

# Function to load data from a file


def extract_timestamp(file_name):
    header, *filename_parts = str(file_name).split('-')
    file_name = str(filename_parts[2])
    header, *split = file_name.split('.')
    return filename_parts[1] + '-' + header

# Function to process sky data based on resolution


def process_data(sky_data, az_start, az_end, el_start, el_end, resolution):
    cleaned_data = sky_data[1:, 1:]
    if resolution == 1:
        cleaned_data = cleaned_data[:, :-1]
        az_range = np.array([az_end, (az_start + az_end) / 2, az_start])
        el_range = np.array([el_end, (el_start + el_end) / 2, el_start])
    elif resolution == 2:
        cleaned_data = cleaned_data[:, :-
                                    (az_end - (az_end - az_start) * 5 - 1)]
        az_range = np.array([az_end, (az_start + az_end) / 2, az_start])
        el_range = np.array([el_end, (el_start + el_end) / 2, el_start])
    else:
        raise NotImplementedError("Medium resolution not implemented yet")
    return cleaned_data, az_range, el_range

# Function to plot heatmap


def plot_heatmap(cleaned_data, az_range, el_range, timestamp):
    x = np.array([0, len(az_range) // 2, len(az_range) - 1])
    y = np.array([0, len(el_range) // 2, len(el_range) - 1])

    plt.xticks(x, az_range)
    plt.yticks(y, el_range)
    plt.imshow(cleaned_data, cmap='CMRmap')
    plt.colorbar(location='bottom', label='RF Signal Strength')
    plt.xlabel("Azimuth (dish uses CCW heading)")
    plt.ylabel("Elevation")
    plt.title(f"Ku Band Scan {timestamp}")
    plt.show()


if __name__ == "__main__":
    file_name = sys.argv[1]
    print('Loading data file.')
    sky_data = load_data(file_name)
    timestamp = extract_timestamp(file_name)

    print('Loading parameters of scan.')
    scan_params = load_data(f"scan-settings-{timestamp}.txt")
    az_start, az_end, el_start, el_end, resolution = map(int, scan_params)

    print('Processing heatmap...')
    cleaned_data, az_range, el_range = process_data(
        sky_data, az_start, az_end, el_start, el_end, resolution)
    plot_heatmap(cleaned_data, az_range, el_range, timestamp)
