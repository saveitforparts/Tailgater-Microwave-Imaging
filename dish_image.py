#Python program to process raw Tailgater scan data from dish_scan.py
#Takes saved text file (numpy array) and converts into heatmap

import numpy as np
import matplotlib.pyplot as plt
import sys


#Open the filename passed at runtime
print('Loading data file.')
with open(sys.argv[1], 'r') as file_name:
	sky_data = np.loadtxt(file_name)

#Pull timestamp from filename (there's probably a better way to do this)
header, *filename_parts = str(file_name).split('-')     
file_name=str(filename_parts[2])
header, *split = file_name.split('.')
timestamp=(filename_parts[1]+'-'+header)

print('Loading parameters of scan.')
scan_params = np.loadtxt("scan-settings-"+timestamp+".txt")
az_start=int(scan_params[0])
az_end=int(scan_params[1])
el_start=int(scan_params[2])
el_end=int(scan_params[3])
resolution=int(scan_params[4])


#print ('az_start=',az_start,' az_end=',az_end,' el_start=',el_start,' el_end=',el_end,' res=',resolution)

if resolution == 1: #standard low resolution
	#Trim off the messy edges of the array (probably an ugly hack)
	cleaned_data = np.delete(sky_data, obj=0, axis=0)
	cleaned_data = np.delete(cleaned_data, obj=0, axis=1)
	cleaned_data = np.delete(cleaned_data, obj=(az_end-az_start-1), axis=1)
	
	#set up custom axis labels
	x=np.array([0,(az_end-az_start-1)/2,az_end-az_start-2])
	az_range=np.array([az_end,(az_start+az_end)/2,az_start])
	plt.xticks(x,az_range)
	y=np.array([0,(el_end-el_start-1)/2,el_end-el_start-1])
	el_range=np.array([el_end,(el_start+el_end)/2,el_start])
	plt.yticks(y,el_range)
	
	
elif resolution == 2:
	#Trim off the messy edges of the array (probably an ugly hack)
	cleaned_data = np.delete(sky_data, obj=0, axis=0)
	cleaned_data = np.delete(cleaned_data, obj=0, axis=1)
	cleaned_data = np.delete(cleaned_data, obj=(az_end-((az_end-az_start)*5)-1), axis=1)
	
	#set up custom axis labels
	x=np.array([0,(((az_end-az_start)*5)-1)/2,((az_end-az_start)*5)-2])
	az_range=np.array([az_end,(az_start+az_end)/2,az_start])
	plt.xticks(x,az_range)
	y=np.array([0,(((el_end-el_start)*5)-1)/2,((el_end-el_start)*5)])
	el_range=np.array([el_end,(el_start+el_end)/2,el_start])
	plt.yticks(y,el_range)

else:
	#medium resolution not implemented yet
	print('')

print('Processing heatmap...')


plt.imshow(cleaned_data, cmap='CMRmap')
plt.colorbar(location='bottom',label='RF Signal Strength')
plt.xlabel("Azimuth (dish uses CCW heading)")
plt.ylabel("Elevation")
plt.title("Ku Band Scan "+timestamp)



plt.show()


