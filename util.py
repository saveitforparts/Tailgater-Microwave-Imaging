from numpy import loadtxt, array, roll
import matplotlib.pyplot as plt

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

# Function to load data from a file


def extract_timestamp(file_name):
    header, *filename_parts = str(file_name).split('-')
    file_name = str(filename_parts[2])
    header, *split = file_name.split('.')
    return filename_parts[1] + '-' + header

def process_data(sky_data, az_start, az_end, el_start, el_end, resolution):
    cleaned_data = sky_data[1:, 1:]
    
    # Apply motor/indexing issue fix
    for row_index in range(el_end - el_start):
        if row_index % 2 == 0:
            cleaned_data[row_index] = roll(cleaned_data[row_index], 3)
    
    if resolution == 1:
        cleaned_data = cleaned_data[:, :-1]
        az_range = array([az_end, (az_start + az_end) / 2, az_start])
        el_range = array([el_end, (el_start + el_end) / 2, el_start])
    elif resolution == 2:
        cleaned_data = cleaned_data[:, :-
                                    (az_end - (az_end - az_start) * 5 - 1)]
        az_range = array([az_end, (az_start + az_end) / 2, az_start])
        el_range = array([el_end, (el_start + el_end) / 2, el_start])
    else:
        raise NotImplementedError("Medium resolution not implemented yet")
    return cleaned_data, az_range, el_range

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