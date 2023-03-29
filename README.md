# tailgater
Microwave imaging using portable "Tailgater" satellite antenna. 

Gabe Emerson / Saveitforparts 2023. Email: gabe@saveitforparts.com

**Introduction:**

This code controls a portable satellite antenna over USB using serial commands. 
The dish_scan.py program aims the dish to a selected portion of the sky and records
the RF signal strength. The dish_image.py program reads the resulting data and 
creates	a heatmap of the scanned area. Frequencies using stock Tailgater antenna 
hardware will be in the Ku band (~11ghz)

Please note that the author is not an expert in Python, Linux, satellites, or 
radio theory! This code is very experimental, amateur, and not optimized. It will
likely void any warranty your Tailgater antenna may have. There are probably better,
faster, and more efficient ways	to do some of the functions and calculations in 
the code. Please feel free to fix, improve, or add to anything (If you do, I'd
love to hear what you did and how it worked!)    


**Applications:**

- Imaging geostationary TV satellites
- Surveying an environment or room for microwave radiation
- Imaging an environment using ambient or reflected microwaves from Ku band source
- Imaging other wavelengths with a different feedhorn or LNB (not tested)
- Integration with an SDR and other antenna elements (not tested) 


**Hardware Requirements:**

This code has been developed and tested with a Dish Network "Tailgater" portable
satellite antenna. Specifically, a 2014 version in an octagonal-ish enclosure 
with a USB "A" connector on the mainboard (located inside the enclosure, behind 
the dish reflector). There are many variations, models, and versions of this 
antenna, including Wallace, VuQube, Dish, King Controls, etc. I have not found a
consistent model numbering scheme, so I don't know how to identify the correct 
model without opening the top and looking for a USB port. Other models have USB
mini or other ports, and some appear to have jumpers for 9-pin serial. I have not 
tested this software on any of those variations.

My test unit uses firmware version "pragelato.h 704 2013-08-09 03:41:27Z rudrava"
Other versions may have different console commands available.

This code has been tested sucessfully on a range of Linux PCs, from 686-class using
a low-resource distro, to higher-end running a modern distribution. 


**Notes on power supply:**

The USB connection only provides data to/from the dish. Power for the board, LNB, and 
motors comes from the coax "F" connector. This needs between 13-18V DC, center pin 
positive. Normally this is provided by a set-top box or satellite reciever. Power can
also be provided by an in-line injector for powered antennas, a meter such as V8 Finder,
or simply a DC adapter wired to a coax cable. Providing 13V will tell the LNB to use
vertical polarity and 18V will use horizontal polarity. 


**Package Requirements:**

dish_scan.py uses the numpy, pyserial and regex packages. dish_image uses matplotlib.
They can be installed individually or by running "pip install -r requirements.txt"


**Setting up / testing Tailgater console:**

To connect to a Tailgater antenna with USB A port, you will need an A-to-A cable
(available online). 

You can check for proper connection by running "lsusb" on Linux. The dish should show
up as "Microchip Technology, Inc. CDC RS-232 Emulation Demo".

Run "dmesg | grep tty" to see which port the dish is using. This is usually something
like /dev/ttyACM0, although I have seen it jump to ttyACM1 or ACM2 if the power or USB
connection are interrupted. If your Tailgater is NOT on /dev/ttyACM0 you will need to 
edit line 15 of dish_scan.py to reflect the correct port. 
	
To connect to the serial console on the dish, run "screen /dev/ttyACM0" (or appropriate
port) on Linux, or use a Windows serial terminal to connect to the usb device (typically
com3 or similar). You will initially get a blank screen. Typing "help" should return a
menu of available commands and a "GO>" prompt. 
	
Note that the console does not accept backspace, so if you make a mistake while typing,
just hit enter to clear the console. If necessary, close the console or unplug the 
dish to avoid a motor overrun. 


**Positioning the dish:**

The Tailgater dish uses a 360-degree counter-clockwise coordinate system, with the coax
/ F connector as "North" / 0 degrees. The dish considers an azimuth of 90 to be 90 degrees
counterclockwise from the coax jack (looking down at the dish from above). Azimuth 180 is
directly opposite the coax jack, and azimuth 270 is 90 degrees clockwise from the RF jack.
This is technically "backwards" from a standard compass heading. The code is written to
take this into account, but please note that image and array outputs will show azimuth in
the dish's reference plane, opposite of standard compass or orbital azimuth. 
		
Generally I place the dish with the coax connector facing due North (for scans of the
Southern sky), but you can place it in any orientation you want. The dish scans left to
right, incrementing up from the starting elevation. Remember the coordinate system is
"backwards" compared to standard compass headings.  


**Running a scan:**

Once the dish is connected, powered, and ready on a USB port, run:
"python3 dish_scan.py"
You will be prompted for the starting and ending azimuth and elevation of your scan. 
Valid azimuth range is 0-360, and valid elevations are 5-70 degrees (outside of these
values may overrun the motors). If you enter a value outside the valid range, the 
program will use the minimum or maximum as appropriate. The default values are from
azimuth 90 to 270 (West to East in the dish's coordinate system), and from elevation 5 
to 70 degrees. This covers most of the Southern sky (if the dish is placed with coax jack
aiming due North). A scan with default values takes approximately 3.5 hours due to the 
minimum rfwatch runtime of 1 second. Scans of smaller azimuth/elevation ranges should take
less time. Estimated scan time for your parameters will be shown once the scan starts. 
	
During the scan, the current azimuth, elevation, and signal strength will be displayed for
each dish position. A preview image, "result-<timestamp>.png" will be created and will 
update live during the scan. On Gnome Image Viewer, this file should automatically refresh as
it updates. It will be very small (x pixels equal to your scan's azimuth range, and y pixels
equal to your scan's elevation range). However, it should be enough to get an idea if the
scan is working. 

	
**Generating an image from a scan:**
	
Once a scan has completed, you will have three output files with the same timestamp:

- "result-<timestamp>.png"         The low-resolution preview image.
	
- "raw-data-<timestamp>.txt"       The raw scan values in a numpy array.
	
- "scan-settings-<timestamp>.txt"  The scan parameters (start and end azimuth / elevation)
	
dish_image.py will use the two text files to create a heatmap of your scan. Run the code 
along with the name of the raw-data scan you want to process. For example:
"python3 dish_image.py raw-data-20230322-153935.txt"
	
The code will load the corresponding scan-settings file automatically, and opens a
heatmap of the scan in a new window. You can save this heatmap for later use. 

I noticed an issue where counterclockwise rows were offset slightly from clockwise rows,
this seems to be a combination of indexing and inconsistencies with motor movements. 
The fix_image.py script is an alternate version of dish_image that outputs a better
bitmap from scans run with my dish. It does this by shifting every other row in the
signal strenth array 3 places to the right. Each Tailgater unit might be a little
different, and the range of elevation values can alter this offset. You may have to play
with the last number on line 38 to get the best image.

	
**Example Images:**
I have included several example images to show what a scan looks like:
	 
- "dish_image example.png"  The result of running a default scan with dish_scan.py and 
processing with dish_image.py. Shows geostationary TV satellites.
				  
- "satellite overlay.png"   The previous file overlaid on a panoramic photo of the same area. 
Note that trees, roof overhangs, and power poles are visible in RF.
				  
- "satellite preview.png"   A scaled-up version of the "result" preview generated during a scan.
	
- "room overlay.png"        An overlay of a default scan run indoors, showing microwave RF
coming from a poorly-shielded PC tower (lower right). 
				  
- "house.png"		  A structure scan comparing KU band (with "hsv" colormap), visible
light, and 50% overlay of each. 
				  
- "tailgater.png"		  Example of the antenna unit used for this project.
		

**Example Files**

I have included some example data files output by dish_scan.py, for processing with dish_image.py

- "raw-data-20230321-193653.txt":   numpy matrix of signal strength at each azimuth and elevation pair

- "scan-settings-20230321-193653.txt":    scan parameters for dish_image to use when processing

- "result-20230321-193653.png":     Preview image created by dish_scan (not used by dish_image)


**Additional notes:**
	
The dish_scan.py code contains code for two resolution settings, however the high setting does
NOT currently work with my dish due to motor drift. Low resolution (default) uses azangle and
elangle commands on the Tailgater console, so each scan position is one degree. The high-
resolution version would have used the "nudge" commands available in the Tailgater console. 
However, these do not seem to be consistent in each direction, so the dish drifts off center 
over the course of a scan and causes a distorted image. Currently the "resolution" setting is 
disabled, you can re-enable it by un-commenting lines 61-64 and commenting out line 66. Do so
at your own risk of frustration and possibly hitting motor limits. 

The heatmap generated by dish_image.py uses CMRmap. If you wish to use another colormap, you can
change line 67 of dish_image.py. I also like "seismic" and "gnuplot2", but I feel that they lose
some definition on the background landscape. "hsv" may also be useful for noisy scans. 
	
If you use this code and encounter any problems, feel free to email me at the address at the top
of this file. However, I may have to refer back to this myself to remember how it works! 

