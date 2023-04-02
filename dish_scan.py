#Python program to scan with Dish Tailgater and output signal strength bitmap
#Gabe Emerson / Saveitforparts 2023, Email: gabe@saveitforparts.com

import serial
import time
from PIL import Image
import regex as re
import numpy as np

#generate timestamp
timestr = time.strftime("%Y%m%d-%H%M%S")

#define "dish" as the serial port device to interface with
dish = serial.Serial(
	port='/dev/ttyACM0',
	baudrate = 9600,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=1)

print ("Serial port connected")
print ('')

#Prompt for scan parameters, with default values and valid range checks
az_start = int(input('Starting Azimuth in degrees (0-360, default 90): ') or 90)

if az_start < 0:
	print('Azimuth out of range, setting to 0')
	az_start=0
if az_start > 360:
	print('Azimuth out of range, setting to 360')
	az_start=360

az_end = int(input('Ending Azimuth in degrees (default 270): ') or 270)
if az_end < 0:
	print('Azimuth out of range, setting to 0')
	az_end=0
if az_end > 360:
	print('Azimuth out of range, setting to 360')
	az_end=360

el_start = int(input('Starting Elevation in degrees (5-70, default 5): ') or 5)
if el_start < 5:
	print('Elevation out of range, setting to 5')
	el_start=5
if el_start > 70:
	print('Elevation out of range, setting to 70')
	el_start=70

el_end = int(input('Ending Elevation in degrees (default 70): ') or 70)
if el_end < 5:
	print('Elevation out of range, setting to 5')
	el_end=5
if el_end > 70:
	print('Elevation out of range, setting to 70')
	el_end=70


#######################################################
#######################################################
#######################################################

import argparse
import sys

def value_in_range(value, min, max):
    if(value >= min and value <= max):
        return True
    else:
        return False


def validate_input(parameter_name, supplied_value, min_value, max_value, default_value):
    parameter_error_text = "Error: supplied parameter {parameter} " +\
                           "[{value}] is out of range [{min}, {max}]; " +\
                           "supply a new value or press enter to use the " +\
                           "default value [{default}] "

    validated_value = default_value # safe placeholder

    while(1):
        this_error = parameter_error_text.format(parameter=parameter_name,
                                                 value=supplied_value,
                                                 min=min_value,
                                                 max=max_value,
                                                 default=default_value)
        error_response = input(this_error)
        
        # Possible outcomes:
        # it's blank - use the default value and continue
        # it's a number - check value against range
        #       if it's in range, use it and continue
        #       if it's out of range, continue the error loop
        # it's not a number - continue the error loop

        supplied_value = error_response # to update error message if necessary

        # handle blank case - use default value and continue
        if(error_response == ""):
            validated_value = default_value
            break

        # check if it can be converted to an int
        try:
            new_value = int(error_response)
            
            if(value_in_range(new_value, min_value, max_value)):
                # good input, use it and continue
                validated_value = new_value
                break
            else:
                # out of range - ask again
                continue

        except ValueError:
            # invalid input - ask again
            continue

    return validated_value


AZ_START_DEFAULT = 90
AZ_END_DEFAULT = 270
EL_START_DEFAULT = 5
EL_END_DEFAULT = 70

AZ_MIN = 0
AZ_MAX = 360
EL_MIN = 5
EL_MAX = 70

parser = argparse.ArgumentParser()

parser.add_argument("--az_start", "-a1", type=int)
parser.add_argument("--az_end", "-a2", type=int)
parser.add_argument("--el_start", "-e1", type=int)
parser.add_argument("--el_end", "-e2", type=int)

args = parser.parse_args()

# Input error handling:
# if setting is out of range, set defaults and ask to continue or cancel
# if end < start, swap values
# if start == end, what happens?

# az_start
if(args.az_start and value_in_range(args.az_start, AZ_MIN, AZ_MAX)):
    az_start = args.az_start
elif(args.az_start):
    az_start = validate_input("az_start", args.az_start, 
                              AZ_MIN, AZ_MAX, AZ_START_DEFAULT)
else:
    az_start = AZ_START_DEFAULT

# az_end
if(args.az_end and value_in_range(args.az_end, AZ_MIN, AZ_MAX)):
    az_end = args.az_end
elif(args.az_end):
    az_end = validate_input("az_end", args.az_end, 
                            AZ_MIN, AZ_MAX, AZ_END_DEFAULT)
else:
    az_end = AZ_END_DEFAULT

# el_start
if(args.el_start and value_in_range(args.el_start, EL_MIN, EL_MAX)):
    el_start = args.el_start
elif(args.el_start):
    el_start = validate_input("el_start", args.el_start, 
                              EL_MIN, EL_MAX, EL_START_DEFAULT)
else:
    el_start = EL_START_DEFAULT

# el_end
if(args.el_end and value_in_range(args.el_end, EL_MIN, EL_MAX)):
    el_end = args.el_end
elif(args.el_end):
    el_end = validate_input("el_end", args.el_end,
                            EL_MIN, EL_MAX, EL_END_DEFAULT)
else:
    el_end = EL_END_DEFAULT

# compare and swap if end > start
if(az_start > az_end):
    temp = az_start
    az_start = az_end
    az_end = temp

if(el_start > el_end):
    temp = el_start
    el_start = el_end
    el_end = temp

# for now if they're equal, error out
error_quit = 0

if(az_start == az_end):
    error_quit = 1
    print("Error - azimuth start and end values are equal")

if(el_start == el_end):
    error_quit = 1
    print("Error - elevation start and end values are equal")

if(error_quit):
    sys.exit()
		


#######################################################
#######################################################
#######################################################

#########This method doesn't work reliably, "nudge" results in too much motor drift on azimuth axis
#Choose between between azangle/elangle for low res and aznudge/elnudge for high res
#resolution = int(input('Resolution (1=low, 2=high, default 1): ') or 1)
#if not resolution in (1,2):
#	print('Unknown selection, setting to 1 (low)')
#	resolution=1 

resolution = 1 #hard-coding this until if/when we figure out reliable motor steps smaller than full degrees


np.savetxt("scan-settings-" + timestr +".txt", (az_start,az_end,el_start,el_end,resolution))	

if resolution==1: #standard scan using angles
	az_range = az_end - az_start
	el_range = el_end - el_start

	#Provide runtime estimate (I'm making a rough guess based on prior runs on two different computers)
	time_est = az_range * el_range
	print ('Estimated scan time with your parameters is ', (time_est+(time_est/6))/60, ' minutes.')
	print ('')

	#create bitmap to preview signal strengths
	sky_image = Image.new('RGB', [az_range+1,el_range+1], 255) 
	data = sky_image.load()

	#create 2D array for raw signal strengths
	sky_data = np.zeros((el_range+1,az_range+1))

	print ("Moving dish to staring position...")
	#initialize starting dish position
	#for some reason, the dish only receives single char from each write(), so send one at a time
	#(wow much kludge, such ugly)
	dish.write(b'a')
	dish.write(b'z')
	dish.write(b'a')
	dish.write(b'n')
	dish.write(b'g')
	dish.write(b'l')
	dish.write(b'e')
	dish.write(b' ')
	angle=str(az_start)
	if (len(angle)==3):
		dish.write(angle[0].encode())
		dish.write(angle[1].encode())
		dish.write(angle[2].encode())
	elif len(angle)==2:
		dish.write(angle[0].encode())
		dish.write(angle[1].encode())
	else: 
	        #single-digit number
	        dish.write(angle.encode())
	dish.write(b'\r')

	time.sleep(5)   #Give motors time to drive dish to scan origin
	dish.flush()
	dish.reset_output_buffer()

	dish.write(b'e')
	dish.write(b'l')
	dish.write(b'a')
	dish.write(b'n')
	dish.write(b'g')
	dish.write(b'l')
	dish.write(b'e')
	dish.write(b' ')
	angle=str(el_start)
	if (len(angle)==3):
		dish.write(angle[0].encode())
		dish.write(angle[1].encode())
		dish.write(angle[2].encode())
	elif len(angle)==2:
	        dish.write(angle[0].encode())
	        dish.write(angle[1].encode())
	else: 
	        #single-digit number
	        dish.write(angle.encode())
	dish.write(b'\r')
	dish.flush()
	dish.reset_output_buffer()
	dish.reset_input_buffer()
	time.sleep(5)
		
	direction=0		
	#aiming loop
	#valid elangle range appears to be ~2-73 degrees, use slightly smaller range to avoid motor overrun. 
	for elevation in range (el_start,el_end):
		direction=direction+1
		#valid azangle 0-360. Remember dish increments ccw. 
		for azimuth in range (az_start,az_end):
	
			if (direction % 2) == 0: 		  #check for sweep direction
				azimuth = abs(azimuth-az_end)+az_start  	  #increment backwards on even numbered loops
				
			print("Azimuth: ", azimuth, ", Elevation: ", elevation)  #display current position

			#command dish to next azimuth	
			dish.write(b'a')
			dish.write(b'z')
			dish.write(b'a')
			dish.write(b'n')
			dish.write(b'g')
			dish.write(b'l')
			dish.write(b'e')
			dish.write(b' ')
			#we have to break up 3 and 2 digit numbers into single characters
			angle=str(azimuth)
			if (len(angle)==3):
			        dish.write(angle[0].encode())
			        dish.write(angle[1].encode())
			        dish.write(angle[2].encode())
			elif len(angle)==2:
			        dish.write(angle[0].encode())
			        dish.write(angle[1].encode())
			else: #shouldn't need this for typical range, but might want it later
			        #single-digit number
			        dish.write(angle.encode())
			dish.write(b'\r')
			
			#this seems necessary to avoid SerialException issue? (probably also kludgy)
			while True:
				try:
					dish.reset_input_buffer() #avoid overflow 
				
					#request signal strength 
					dish.write(b'r')
					dish.write(b'f')
					dish.write(b'w')
					dish.write(b'a')
					dish.write(b't')
					dish.write(b'c')
					dish.write(b'h')
					dish.write(b' ')
					dish.write(b'1')
					dish.write(b'\r')
		
					dish.flush()
					dish.reset_output_buffer()
	                		                					                    
					reply = dish.read(207).decode().strip()      #read dish response
					header, *readings = reply.split('[5D')       #Split into list of signal strengths
					output = readings[0]			     #grab first list element
					output = re.sub(r'\p{C}', '', output)        #remove any control chars
					output = re.sub('[^\d]', '', output).strip() #clean up partial garbage
	
					signal_strength = int(output)                #convert to integer
	
				except serial.SerialException as e:
					#dish hasn't replied yet
					time.sleep(0.1)
					continue
				else:
					print('')
				break
	
			print('Signal: ', signal_strength)    #display signal strength
	
			#record raw data to array
			sky_data[abs(elevation-el_end),abs(azimuth-az_end)]=signal_strength
			#write to text file
			np.savetxt(f"raw-data-" + timestr +".txt", sky_data)
			
			#create preview bitmap	
			image_x = abs(azimuth-az_end)    #write bitmap the same way the dish is scanning
			image_y = abs(elevation-el_end)   #write bitmap the same way the dish is scanning
			data[image_x,image_y] = (signal_strength % 255,	0, 0)
			#write bitmap to time stamped image file
			sky_image.save('result-' + timestr +'.png')


		#command dish to next elevation
		dish.write(b'e')
		dish.write(b'l')
		dish.write(b'a')
		dish.write(b'n')
		dish.write(b'g')
		dish.write(b'l')
		dish.write(b'e')
		dish.write(b' ')
		#We have to break up 2 digit numbers into single characters
		angle=str(elevation)
		if len(angle)==2: #will only ever have 1 and 2-digit elevations
		        dish.write(angle[0].encode())
		        dish.write(angle[1].encode())
		else: 
		        #single-digit number
		        dish.write(angle.encode())
		dish.write(b'\r')

#####################################Currently resolution 2 is not enabled, because "nudge" isn't consistent
elif resolution==2: #high res scan using nudge instead of angle

	#"nudge" is "about 0.2 degrees", so for each degree in range we have 5 dish positions
	az_range = (az_end - az_start)*5
	el_range = (el_end - el_start)*5

	#Provide runtime estimate (I'm making a rough guess based on prior runs on two different computers)
	time_est = az_range * el_range
	print ('Estimated scan time with your parameters is ', (time_est+(time_est/6))/60, ' minutes.')
	print ('')

	#create bitmap to preview signal strengths
	sky_image = Image.new('RGB', [az_range+1,el_range+1], 255) 
	data = sky_image.load()

	#create 2D array for raw signal strengths
	sky_data = np.zeros((el_range+1,az_range+1))

	print ("Moving dish to staring position...")
	#initialize starting dish position
	#for some reason, the dish only receives single char from each write(), so send one at a time
	#(wow much kludge, such ugly)
	dish.write(b'a')
	dish.write(b'z')
	dish.write(b'a')
	dish.write(b'n')
	dish.write(b'g')
	dish.write(b'l')
	dish.write(b'e')
	dish.write(b' ')
	angle=str(az_start)
	if (len(angle)==3):
		dish.write(angle[0].encode())
		dish.write(angle[1].encode())
		dish.write(angle[2].encode())
	elif len(angle)==2:
		dish.write(angle[0].encode())
		dish.write(angle[1].encode())
	else: 
	        #single-digit number
	        dish.write(angle.encode())
	dish.write(b'\r')

	time.sleep(5)   #Give motors time to drive dish to scan origin
	dish.flush()
	dish.reset_output_buffer()

	dish.write(b'e')
	dish.write(b'l')
	dish.write(b'a')
	dish.write(b'n')
	dish.write(b'g')
	dish.write(b'l')
	dish.write(b'e')
	dish.write(b' ')
	angle=str(el_start)
	if (len(angle)==3):
		dish.write(angle[0].encode())
		dish.write(angle[1].encode())
		dish.write(angle[2].encode())
	elif len(angle)==2:
	        dish.write(angle[0].encode())
	        dish.write(angle[1].encode())
	else: 
	        #single-digit number
	        dish.write(angle.encode())
	dish.write(b'\r')
	dish.flush()
	dish.reset_output_buffer()
	dish.reset_input_buffer()
	time.sleep(5)
	direction=0		
					
	#aiming loop
	#valid elangle range appears to be ~2-73 degrees, use slightly smaller range to avoid motor overrun. 
	for elevation in range (0,el_range):
		direction = direction+1
		#valid azangle 0-360. Remember dish increments ccw. 
		for azimuth in range (0,az_range):
	
			if (direction % 2) == 0: 		  #check for sweep direction
				azimuth = (abs(azimuth-az_range))  	  #increment backwards on even numbered loops
				
			print("X: ", azimuth, ", Y: ", elevation)  #display current position

			#command dish to next azimuth	
			dish.write(b'a')
			dish.write(b'z')
			dish.write(b'n')
			dish.write(b'u')
			dish.write(b'd')
			dish.write(b'g')
			dish.write(b'e')
			dish.write(b' ')
			dish.write(b'c')
			if not (direction % 2) == 0: 		  #check for sweep direction
				dish.write(b'c')			
			dish.write(b'w')
			dish.write(b'\r')
			
			#this seems necessary to avoid SerialException issue? (probably also kludgy)
			while True:
				try:
					dish.reset_input_buffer() #avoid overflow 
				
					#request signal strength 
					dish.write(b'r')
					dish.write(b'f')
					dish.write(b'w')
					dish.write(b'a')
					dish.write(b't')
					dish.write(b'c')
					dish.write(b'h')
					dish.write(b' ')
					dish.write(b'1')
					dish.write(b'\r')
		
					dish.flush()
					dish.reset_output_buffer()
	                		                					                    
					reply = dish.read(207).decode().strip()      #read dish response
					header, *readings = reply.split('[5D')       #Split into list of signal strengths
					output = readings[0]			     #grab first list element
					output = re.sub(r'\p{C}', '', output)        #remove any control chars
					output = re.sub('[^\d]', '', output).strip() #clean up partial garbage
	
					signal_strength = int(output)                #convert to integer
	
				except serial.SerialException as e:
					#dish hasn't replied yet
					time.sleep(0.1)
					continue
				else:
					print('')
				break
	
			print('Signal: ', signal_strength)    #display signal strength
	
			#record raw data to array
			sky_data[abs(elevation-el_range),abs(azimuth-az_range)]=signal_strength
			#write to text file
			np.savetxt(f"raw-data-" + timestr +".txt", sky_data)
			
			#create preview bitmap	
			image_x = abs(azimuth-az_range)    #write bitmap the same way the dish is scanning
			image_y = abs(elevation-el_range)   #write bitmap the same way the dish is scanning
			data[image_x,image_y] = (signal_strength % 255,	0, 0)
			#write bitmap to time stamped image file
			sky_image.save('result-' + timestr +'.png')
			
			
		#command dish to next elevation
		dish.write(b'e')
		dish.write(b'l')
		dish.write(b'n')
		dish.write(b'u')
		dish.write(b'd')
		dish.write(b'g')
		dish.write(b'e')
		dish.write(b' ')
		dish.write(b'u')
		dish.write(b'p')
		dish.write(b'\r')	
##################################Resolution 2 not working, ignore above elif

else: #possibly implement medium resolution in the future?
	print ('')

print ('Scan complete!')
#close serial connection
dish.close()

