# Python program to scan with Dish Tailgater and output signal strength bitmap
# Gabe Emerson / Saveitforparts 2023, Email: gabe@saveitforparts.com

import numpy as np
from PIL import Image

from lib.console_messages import error, info
from lib.dish_commands import DishCommands
from lib.questions import get_valid_int
from lib.time_formatting import timestamp

startup_timestamp = timestamp()

PRINT_DEBUG = True
PRINT_INFO = True

dish_cmd = DishCommands()


def writeout_results():
	global sky_data
	global signal_strength
	global startup_timestamp
	
	# record raw data to array
	sky_data[abs(elevation - el_end), abs(azimuth - az_end)] = signal_strength
	# write to text file
	np.savetxt(f"raw-data-" + startup_timestamp + ".txt", sky_data)
	
	# create preview bitmap
	image_x = abs(azimuth - az_end)  # write bitmap the same way the dish is scanning
	image_y = abs(elevation - el_end)  # write bitmap the same way the dish is scanning
	data[image_x, image_y] = (signal_strength % 255, 0, 0)
	# write bitmap to time stamped image file
	sky_image.save('result-' + startup_timestamp + '.png')


# Prompt for scan parameters, with default values and valid range checks

az_start = get_valid_int("minimum Azimuth (in degrees)", 90, minimum=0, maximum=360)
az_end = get_valid_int("maximum Azimuth (in degrees)", 270, minimum=0, maximum=360)
el_start = get_valid_int("minimum Elevation (in degrees)", 5, minimum=5, maximum=70)
el_end = get_valid_int("maximum Elevation (in degrees)", 70, minimum=5, maximum=70)

if az_start > az_end:
	error("the minimal Azimuth must be smaller than the maximum")
if el_start > el_end:
	error("the minimal elevation must be smaller than the maximum")

#########This method doesn't work reliably, "nudge" results in too much motor drift on azimuth axis
# Choose between between azangle/elangle for low res and aznudge/elnudge for high res
# resolution = int(input('Resolution (1=low, 2=high, default 1): ') or 1)
# if not resolution in (1,2):
#	print('Unknown selection, setting to 1 (low)')
#	resolution=1 

resolution = 1  # hard-coding this until if/when we figure out reliable motor steps smaller than full degrees

np.savetxt("scan-settings-" + startup_timestamp + ".txt", (az_start, az_end, el_start, el_end, resolution))

if resolution == 1:  # standard scan using angles
	az_range = az_end - az_start
	el_range = el_end - el_start
	
	# Provide runtime estimate (I'm making a rough guess based on prior runs on two different computers)
	time_est = az_range * el_range
	info('Estimated scan time with your parameters is ', (time_est + (time_est / 6)) / 60, ' minutes.\n')
	
	# create bitmap to preview signal strengths
	sky_image = Image.new('RGB', [az_range + 1, el_range + 1], 255)
	data = sky_image.load()
	
	# create 2D array for raw signal strengths
	sky_data = np.zeros((el_range + 1, az_range + 1))
	
	# move dish to start position
	dish_cmd.init_dish_position(az_start, el_start)
	
	direction = 0
	# aiming loop
	# valid elangle range appears to be ~2-73 degrees, use slightly smaller range to avoid motor overrun.
	for elevation in range(el_start, el_end):
		direction = direction + 1
		# valid azangle 0-360. Remember dish increments ccw.
		for azimuth in range(az_start, az_end):
			
			if (direction % 2) == 0:  # check for sweep direction
				azimuth = abs(azimuth - az_end) + az_start  # increment backwards on even numbered loops
			
			info("Azimuth: ", azimuth, ", Elevation: ", elevation)  # display current position
			
			# command dish to next azimuth
			dish_cmd.goto_azimuth(azimuth)
			
			signal_strength = dish_cmd.get_signal_strength()
			
			info('Signal: %i' % signal_strength)  # display signal strength
			
			writeout_results()
		
		# command dish to next elevation
		dish_cmd.goto_elevation(elevation)

#####################################Currently resolution 2 is not enabled, because "nudge" isn't consistent
elif resolution == 2:  # high res scan using nudge instead of angle
	
	# "nudge" is "about 0.2 degrees", so for each degree in range we have 5 dish positions
	az_range = (az_end - az_start) * 5
	el_range = (el_end - el_start) * 5
	
	# Provide runtime estimate (I'm making a rough guess based on prior runs on two different computers)
	time_est = az_range * el_range
	print('Estimated scan time with your parameters is ', (time_est + (time_est / 6)) / 60, ' minutes.')
	print('')
	
	# create bitmap to preview signal strengths
	sky_image = Image.new('RGB', [az_range + 1, el_range + 1], 255)
	data = sky_image.load()
	
	# create 2D array for raw signal strengths
	sky_data = np.zeros((el_range + 1, az_range + 1))
	
	dish_cmd.init_dish_position(az_start, el_start)
	
	direction = 0
	
	# aiming loop
	# valid elangle range appears to be ~2-73 degrees, use slightly smaller range to avoid motor overrun.
	for elevation in range(0, el_range):
		direction = direction + 1
		# valid azangle 0-360. Remember dish increments ccw.
		for azimuth in range(0, az_range):
			
			if (direction % 2) == 0:  # check for sweep direction
				azimuth = (abs(azimuth - az_range))  # increment backwards on even numbered loops
			
			print("X: ", azimuth, ", Y: ", elevation)  # display current position
			
			if not (direction % 2) == 0:
				dish_cmd.nudge_right()
			else:
				dish_cmd.nudge_left()
			
			signal_strength = dish_cmd.get_signal_strength()
			
			print('Signal: ', signal_strength)  # display signal strength
			
			writeout_results()
		
		# command dish to next elevation
		dish_cmd.nudge_up()

##################################Resolution 2 not working, ignore above elif

else:  # possibly implement medium resolution in the future?
	print('')

info('Scan complete!')
# close serial connection
dish_cmd.close_conn()
