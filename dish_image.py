import sys
import util

if __name__ == "__main__":
    file_name = sys.argv[1]
    print('Loading data file.')
    sky_data = util.load_data(file_name)
    timestamp = util.extract_timestamp(file_name)

    print('Loading parameters of scan.')
    scan_params = util.load_data(f"scan-settings-{timestamp}.txt")
    az_start, az_end, el_start, el_end, resolution = map(int, scan_params)

    print('Processing heatmap...')
    cleaned_data, az_range, el_range = util.process_data(
        sky_data, az_start, az_end, el_start, el_end, resolution)
    util.plot_heatmap(cleaned_data, az_range, el_range, timestamp)
