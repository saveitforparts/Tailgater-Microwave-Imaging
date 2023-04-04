import serial
import time
from PIL import Image
import regex as re
import numpy as np
import util

# Generate timestamp
timestr = time.strftime("%Y%m%d-%H%M%S")

# Define "dish" as the serial port device to interface with
dish = serial.Serial(
    port='/dev/ttyACM0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

print("Serial port connected\n")

az_start = util.input_with_range_check(
    'Starting Azimuth in degrees (0-360, default 90): ', 90, 0, 360)
az_end = util.input_with_range_check(
    'Ending Azimuth in degrees (default 270): ', 270, 0, 360)
el_start = util.input_with_range_check(
    'Starting Elevation in degrees (5-70, default 5): ', 5, 5, 70)
el_end = util.input_with_range_check(
    'Ending Elevation in degrees (default 70): ', 70, 5, 70)

# Hard-coding this until if/when we figure out reliable motor steps smaller than full degrees
resolution = 1

np.savetxt(f"scan-settings-{timestr}.txt",
           (az_start, az_end, el_start, el_end, resolution))

if resolution == 1:
    az_range = az_end - az_start
    el_range = el_end - el_start

    time_est = az_range * el_range
    print(
        f'Estimated scan time with your parameters is {(time_est + (time_est / 6)) / 60} minutes.\n')

    sky_image = Image.new('RGB', [az_range + 1, el_range + 1], 255)
    data = sky_image.load()

    sky_data = np.zeros((el_range + 1, az_range + 1))

    print("Moving dish to starting position...")

    util.send_dish_command(dish, 'azangle', az_start)
    time.sleep(5)
    dish.flush()
    dish.reset_output_buffer()

    util.send_dish_command(dish, 'elangle', el_start)
    time.sleep(5)
    dish.flush()
    dish.reset_output_buffer()
    dish.reset_input_buffer()

    direction = 0
    for elevation in range(el_start, el_end):
        direction += 1
        for azimuth in range(az_start, az_end):
            if direction % 2 == 0:
                azimuth = abs(azimuth - az_end) + az_start

            print(f"Azimuth: {azimuth}, Elevation: {elevation}")

            util.send_dish_command(dish, 'azangle', azimuth)

            while True:
                try:
                    dish.reset_input_buffer()

                    util.send_dish_command(dish, 'rfwatch 1')

                    dish.flush()
                    dish.reset_output_buffer()

                    reply = dish.read(207).decode().strip()
                    header, *readings = reply.split('[5D')
                    output = readings[0]
                    output = re.sub(r'\p{C}', '', output)
                    output = re.sub('[^\d]', '', output).strip()

                    signal_strength = int(output)

                except serial.SerialException as e:
                    time.sleep(0.1)
                    continue
                else:
                    print('')
                break

            print(f'Signal: {signal_strength}')

            sky_data[abs(elevation - el_end),
                     abs(azimuth - az_end)] = signal_strength
            np.savetxt(f"raw-data-{timestr}.txt", sky_data)

            image_x = abs(azimuth - az_end)
            image_y = abs(elevation - el_end)
            data[image_x, image_y] = (signal_strength % 255, 0, 0)
            sky_image.save(f'result-{timestr}.png')

        util.send_dish_command('elangle', elevation)

else:
    print('')

print('Scan complete!')
dish.close()
