import sys
import util
from numpy import array

# Function to process sky data based on resolution
def process_data(sky_data, az_start, az_end, el_start, el_end, resolution):
    cleaned_data = sky_data[1:, 1:]
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


if __name__ == "__main__":
    file_name = sys.argv[1]
    print('Loading data file.')
    sky_data = util.load_data(file_name)
    timestamp = util.extract_timestamp(file_name)

    print('Loading parameters of scan.')
    scan_params = util.load_data(f"scan-settings-{timestamp}.txt")
    az_start, az_end, el_start, el_end, resolution = map(int, scan_params)

    print('Processing heatmap...')
    cleaned_data, az_range, el_range = process_data(
        sky_data, az_start, az_end, el_start, el_end, resolution)
    util.plot_heatmap(cleaned_data, az_range, el_range, timestamp)
