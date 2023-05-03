#Python program to scan with Dish Tailgater and output signal strength bitmap
#Version 2.0
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


#######################################################
################## Input validation ###################
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

program_description = "Program to scan with Dish Tailgater " +\
                      "and output signal strength bitmap"

az_start_help = "start azimuth: valid between {} and {}, default = {}".format(
                    AZ_MIN, AZ_MAX, AZ_START_DEFAULT)
az_end_help = "end azimuth: valid between {} and {}, default = {}".format(
                    AZ_MIN, AZ_MAX, AZ_END_DEFAULT)
el_start_help = "start elevation: valid between {} and {}, default = {}".format(
                    EL_MIN, EL_MAX, EL_START_DEFAULT)
el_end_help = "end elevation: valid between {} and {}, default = {}".format(
                    EL_MIN, EL_MAX, EL_END_DEFAULT)

parser = argparse.ArgumentParser(description=program_description)

parser.add_argument("--az_start", "-a1", type=int, help=az_start_help)
parser.add_argument("--az_end", "-a2", type=int, help=az_end_help)
parser.add_argument("--el_start", "-e1", type=int, help=el_start_help)
parser.add_argument("--el_end", "-e2", type=int, help=el_end_help)

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




#Choose between between azangle/elangle for low res and aznudge/elnudge for high res
resolution = int(input('Resolution (1=low, 2=high, default 1): ') or 1)
if not resolution in (1,2):
	print('Unknown selection, setting to 1 (low)')
	resolution=1 


np.savetxt("scan-settings-" + timestr +".txt", (az_start,az_end,el_start,el_end,resolution))	

if resolution==1: #standard scan using angles
	az_range = az_end - az_start
	el_range = el_end - el_start

	#Provide runtime estimate (I'm making a rough guess based on prior runs on two different computers)
	time_est = az_range * el_range
	time_output = (time_est+(time_est/6))/60
	time_output = round(time_output, 2)
	if time_output > 60:
		print ('Estimated scan time with your parameters is ', time_output/60, ' hours.')
	else:
		print ('Estimated scan time with your parameters is ', time_output, ' minutes.')
	print ('')
	user_confirm = input('Proceed with scan? (y/n):')
	if user_confirm.lower().startswith("y"):
		print ('Scan in progress...')
	else:
		print ('exiting.')
		exit()

	#create bitmap to preview signal strengths
	sky_image = Image.new('RGB', [az_range+1,el_range+1], 255) 
	data = sky_image.load()

	#create 2D array for raw signal strengths
	sky_data = np.zeros((el_range+1,az_range+1))

	print ("Moving dish to starting position...")
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

	time.sleep(10)   #Give motors time to drive dish to scan origin
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
	time.sleep(10)
		
	direction=0		
	#aiming loop
	#valid elangle range appears to be ~2-73 degrees, use slightly smaller range to avoid motor overrun. 
	for elevation in range (el_start,el_end):
		direction=direction+1
		#valid azangle 0-360. Remember dish increments ccw. 
		for azimuth in range (az_start,az_end):
	
			#Eliminated alternate scan directions in version 2.0. It was slightly faster,
			#But caused too many indexing and gear meshing issues. 
			#if (direction % 2) == 0:   #check for sweep direction
			#	azimuth = abs(azimuth-az_end)+az_start   #increment backwards on even numbered loops
				
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



		#Move dish slightly farther to allow gear meshing 	
		#if (direction % 2) == 0:
		#	angle = str(int(angle) - 2)
		#else:
		#	angle = str(int(angle) + 2)
		#dish.write(b'a')
		#dish.write(b'z')
		#dish.write(b'a')
		#dish.write(b'n')
		#dish.write(b'g')
		#dish.write(b'l')
		#dish.write(b'e')
		#dish.write(b' ')
		#we have to break up 3 and 2 digit numbers into single characters
		#if (len(angle)==3):
		#        dish.write(angle[0].encode())
		#        dish.write(angle[1].encode())
		#        dish.write(angle[2].encode())
		#elif len(angle)==2:
		#        dish.write(angle[0].encode())
		#        dish.write(angle[1].encode())
		#else: #shouldn't need this for typical range, but might want it later
		        #single-digit number
		#        dish.write(angle.encode())
		#dish.write(b'\r')
		#time.sleep(2)
		
		
		
		#Return to starting azimuth for each elevation position
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
		
		#delay to allow dish to return to starting azimuth, dynamic based on az_range
		wait_time = int((az_range)*0.05)+1 #Dish takes ~0.05sec to rotate 1 degree, plus 1 sec buffer
		time.sleep(wait_time)
		
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


elif resolution==2: #high res scan using nudge instead of angle

	#"nudge" is "about 0.2 degrees" azimuth and about 0.33 degrees elevation
	#So for each degree in Az range we have 5 dish positions, and for each degree in El we have 3 positions. 
	az_range = (az_end - az_start)*5
	el_range = (el_end - el_start)*3

	#Provide runtime estimate (I'm making a rough guess based on prior runs on two different computers)
	time_est = az_range * el_range
	time_output = ((time_est+(time_est/6))/60)+((el_range*10)/60) #High-res takes longer, returns to az_start on each elevation
	time_output = round(time_output, 2)
	if time_output > 60:
		print ('Estimated scan time with your parameters is ', time_output/60, ' hours.')
	else:
		print ('Estimated scan time with your parameters is ', time_output, ' minutes.')
	print ('')
	user_confirm = input('Proceed with scan? (y/n):')
	if user_confirm.lower().startswith("y"):
		print ('Scan in progress...')
	else:
		print ('exiting.')
		exit()
		

	#create bitmap to preview signal strengths
	sky_image = Image.new('RGB', [az_range+1,el_range+1], 255) 
	data = sky_image.load()

	#create 2D array for raw signal strengths
	sky_data = np.zeros((el_range+1,az_range+1))

	print ("Moving dish to starting position...")
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

	time.sleep(10)   #Give motors time to drive dish to scan origin
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
	time.sleep(10)
					
	#aiming loop
	#valid elangle range appears to be ~2-73 degrees, use slightly smaller range to avoid motor overrun. 
	for elevation in range (0,el_range):
		#valid azangle 0-360. Remember dish increments ccw. 
		
		
		for azimuth in range (0,az_range):
	
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
			
		#Return to starting azimuth for each elevation position
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
		
		#delay to allow dish to return to starting azimuth, dynamic based on az_range
		wait_time = int((az_range/5)*0.05)+1 #Dish takes ~0.05sec to rotate 1 degree, plus 1 sec buffer
		time.sleep(wait_time)
		
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
		
		


else: #possibly implement medium resolution in the future?
	print ('Invalid resolution')

print ('Scan complete!')
#close serial connection
dish.close()

