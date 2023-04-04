import sys
import util
from numpy import array

def process_data(sky_data, az_start, az_end, el_start, el_end, resolution):
    # Trim the messy edges of the array
    cleaned_data = sky_data[1:, 1:]
    cleaned_data = cleaned_data[:, :-1]

    # Shift every other row of matrix to fix motor/indexing issue
    for row_index in range(el_end - el_start):
        if row_index % 2 == 0:
            cleaned_data[row_index] = np.roll(cleaned_data[row_index], 3)

    # Calculate the azimuth and elevation range
    az_range = array([az_end, (az_start + az_end) / 2, az_start])
    el_range = array([el_end, (el_start + el_end) / 2, el_start])

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
