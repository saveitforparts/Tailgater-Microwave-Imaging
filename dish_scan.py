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

