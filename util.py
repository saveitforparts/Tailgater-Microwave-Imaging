from numpy import loadtxt, array, roll
import matplotlib.pyplot as plt

# Send a command to the dish


def send_dish_command(dish, command, value):
    for char in command.encode():
        dish.write(bytes([char]))
    dish.write(b' ')
    value = str(value)
    for char in value.encode():
        dish.write(bytes([char]))
    dish.write(b'\r')

# Prompt for scan parameters, with default values and valid range checks


def input_with_range_check(prompt, default, min_val, max_val):
    value = int(input(prompt) or default)
    value = max(min_val, min(value, max_val))
    if value != int(default):
        print(f"Value out of range, setting to {value}")
    return value

# Function to load data from a file


def load_data(file_name):
    with open(file_name, 'r') as f:
        return loadtxt(f)

# Function to extract timestamp from file name


def extract_timestamp(file_name):
    header, *filename_parts = str(file_name).split('-')
    file_name = str(filename_parts[2])
    header, *split = file_name.split('.')
    return filename_parts[1] + '-' + header

# Function to plot heatmap


def plot_heatmap(cleaned_data, az_range, el_range, timestamp):
    x = array([0, len(az_range) // 2, len(az_range) - 1])
    y = array([0, len(el_range) // 2, len(el_range) - 1])

    plt.xticks(x, az_range)
    plt.yticks(y, el_range)
    plt.imshow(cleaned_data, cmap='CMRmap')
    plt.colorbar(location='bottom', label='RF Signal Strength')
    plt.xlabel("Azimuth (dish uses CCW heading)")
    plt.ylabel("Elevation")
    plt.title(f"Ku Band Scan {timestamp}")
    plt.show()
