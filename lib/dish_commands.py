from time import sleep

import regex as re
from serial import SerialException

from console_messages import debug, error, info, warning
from dish_serial import DishDevice

MOTION_TIME_360_AZIMUTH = 5
MINIMAL_MOTION_TIME_AZIMUTH = 0.2
NUDGE_MOTION_TIME_AZIMUTH = 0.2

MOTION_TIME_180_ELEVATION = 5
MINIMAL_MOTION_TIME_ELEVATION = 0.2
NUDGE_MOTION_TIME_ELEVATION = 0.2

MINIMAL_AZIMUTH_INPUT = 0
MAXIMAL_AZIMUTH_INPUT = 359

MINIMAL_ELEVATION_INPUT = -179
MAXIMAL_ELEVATION_INPUT = 179

NUDGE_AZIMUTH_DEGREE = 0.2
NUDGE_ELEVATION_DEGREE = 0.2

# if set to true, the degrees will be flipped right before sending to the hardware
AZIMUTH_DEGREES_FLIPPED = True


class DishCommands():
	def __init__(self):
		self._dish = DishDevice()
		self._position_initiated = False
		self._position_azimuth_accurate = False
		self._position_elevation_accurate = False
		self._position_azimuth = None
		self._position_elevation = None
		self._nudge_left_count = 0
		self._nudge_right_count = 0
		self._nudge_up_count = 0
		self._nudge_down_count = 0
		
		try:
			self._dish.init_serial()
		except:
			error("Could not connect serial port")
		else:
			debug("Serial port connected\n")
	
	def get_position(self) -> tuple[float, float]:
		if not self._position_initiated:
			error("dish_commands.get_position() can't provide info without initiation")
		
		return float(self._position_azimuth + (self._nudge_right_count - self._nudge_left_count) * 0.2), \
			float(self._position_elevation + (self._nudge_up_count - self._nudge_down_count) * 0.2)
	
	def get_int_position(self) -> tuple[int, int] | None:
		if not self._position_initiated:
			error("dish_commands.get_int_position() can't provide info without initiation")
		
		if not self.position_accurate():  # returns None, if int precision isn't enough
			return None
		return self._position_azimuth, self._position_elevation
	
	def position_accurate(self) -> bool:
		if not self._position_initiated:
			error("dish_commands.position_accurate() can't provide info without initiation")
		
		if self._position_azimuth_accurate and self._position_elevation_accurate:
			return True
		return False
	
	def get_signal_strength(self):
		
		signal_strength = -1
		reply = ""
		
		# this seems necessary to avoid SerialException issue? (probably also kludgy)
		while True:
			try:
				self._dish.reset_input_buffer()  # avoid overflow
				
				# request signal strength
				self._dish.write("rfwatch 1\r")
				
				self._dish.flush()
				self._dish.reset_output_buffer()
				
				reply = self._dish.read(207).decode().strip()  # read dish response
			
			except SerialException as e:
				# dish hasn't replied yet
				sleep(0.1)
				continue
			else:
				print('')
			break
		
		if reply != "":
			header, *readings = reply.split('[5D')  # Split into list of signal strengths
			output = readings[0]  # grab first list element
			output = re.sub(r'\p{C}', '', output)  # remove any control chars
			output = re.sub('[^\d]', '', output).strip()  # clean up partial garbage
			
			try:
				signal_strength = int(output)  # convert to integer
			except ValueError:
				signal_strength = -1
		else:
			warning("signal strength report unexpectedly empty")
		
		if signal_strength == -1:
			warning("signal strength could not be determined")
		
		return signal_strength
	
	def _set_azimuth_position(self, azimuth: int):
		self._position_azimuth = azimuth
		self._position_azimuth_accurate = True
		self._nudge_left_count = 0
		self._nudge_right_count = 0
	
	def _set_elevation_position(self, elevation: int):
		self._position_elevation = elevation
		self._position_elevation_accurate = True
		self._nudge_up_count = 0
		self._nudge_down_count = 0
	
	def goto_azimuth(self, azimuth: int):
		if not self._position_initiated:
			error("dish_commands.goto_azimuth() can't got to specific azimuth without initiation")
		
		if not self._check_input_azimuth(azimuth):
			error(
				"dish_commands.goto_azimuth() can't accept azimuth '%i' - out of bound (%i-%i)" % (azimuth, MINIMAL_AZIMUTH_INPUT,
				                                                                                   MAXIMAL_AZIMUTH_INPUT)
				)
		
		distance = abs(self._position_azimuth - azimuth)
		
		if distance > 0 or not self._position_azimuth_accurate:
			self._send_azimuth(azimuth)
			# wait appropriate time for the requested distance of movement
			wait_time = MOTION_TIME_360_AZIMUTH * (distance / 360)
			if wait_time < MINIMAL_MOTION_TIME_AZIMUTH:
				wait_time = MINIMAL_MOTION_TIME_AZIMUTH
			sleep(wait_time)
			
			self._set_azimuth_position(azimuth)
		else:
			warning("requested azimuth was already established")
	
	def goto_elevation(self, elevation: int):
		if not self._position_initiated:
			error("dish_commands.goto_elevation() can't got to specific elevation without initiation")
		
		if not self._check_input_elevation(elevation):
			error(
				"dish_commands.goto_elevation() can't accept elevation '%i' - out of bound (%i-%i)" % (elevation, MINIMAL_ELEVATION_INPUT,
				                                                                                       MAXIMAL_ELEVATION_INPUT)
				)
		
		distance = abs(self._position_elevation - elevation)
		
		if distance > 0 or not self._position_elevation_accurate:
			self._send_elevation(elevation)
			# wait appropriate time for the requested distance of movement
			
			wait_time = MOTION_TIME_180_ELEVATION * (distance / 180)
			if wait_time < MINIMAL_MOTION_TIME_ELEVATION:
				wait_time = MINIMAL_MOTION_TIME_ELEVATION
			sleep(wait_time)
			
			self._set_elevation_position(elevation)
		else:
			warning("requested elevation was already established")
	
	def _check_input_azimuth(self, azimuth: int) -> bool:
		if MINIMAL_AZIMUTH_INPUT <= azimuth <= MAXIMAL_AZIMUTH_INPUT:
			return True
		return False
	
	def _check_input_elevation(self, elevation: int) -> bool:
		if MINIMAL_ELEVATION_INPUT <= elevation <= MAXIMAL_ELEVATION_INPUT:
			return True
		return False
	
	def _send_azimuth(self, azimuth: int, flush=True):
		
		if AZIMUTH_DEGREES_FLIPPED:
			azimuth = abs(azimuth - 360)
			if azimuth == 360:
				azimuth = 0
		
		self._dish.write("azangle %i\r" % azimuth)
		
		if flush:
			self._dish.flush()
			self._dish.reset_output_buffer()
	
	def _send_elevation(self, elevation: int, flush=True):
		self._dish.write("elangle %i\r" % elevation)
		
		if flush:
			self._dish.flush()
			self._dish.reset_output_buffer()
			self._dish.reset_input_buffer()
	
	def goto_xy(self, azimuth: int, elevation: int) -> None:
		
		if not self._position_initiated:
			error("dish_commands.goto_xy() can't got to specific xy without initiation")
		
		if not self._check_input_azimuth(azimuth):
			error(
				"dish_commands.goto_xy() can't accept azimuth '%i' - out of bound (%i-%i)" % (azimuth, MINIMAL_AZIMUTH_INPUT,
				                                                                              MAXIMAL_AZIMUTH_INPUT)
				)
		
		if not self._check_input_elevation(elevation):
			error(
				"dish_commands.goto_xy() can't accept elevation '%i' - out of bound (%i-%i)" % (elevation, MINIMAL_ELEVATION_INPUT,
				                                                                                MAXIMAL_ELEVATION_INPUT)
				)
		
		self.goto_azimuth(azimuth)
		
		self.goto_elevation(elevation)
	
	def init_dish_position(self, azimuth: int, elevation: int) -> None:
		
		if not self._check_input_azimuth(azimuth):
			error(
				"dish_commands.init_dish_position() can't accept azimuth '%i' - out of bound (%i-%i)" % (azimuth, MINIMAL_AZIMUTH_INPUT,
				                                                                                         MAXIMAL_AZIMUTH_INPUT)
				)
		
		if not self._check_input_elevation(elevation):
			error(
				"dish_commands.init_dish_position() can't accept elevation '%i' - out of bound (%i-%i)" % (elevation,
				                                                                                           MINIMAL_ELEVATION_INPUT,
				                                                                                           MAXIMAL_ELEVATION_INPUT)
				)
		info("Moving dish to staring position. Please wait...")
		
		self._send_azimuth(azimuth)
		sleep(5)  # Give motors time to drive dish to scan origin
		
		self._set_azimuth_position(azimuth)
		
		self._send_elevation(elevation)
		sleep(5)
		
		self._set_elevation_position(elevation)
		
		self._position_initiated = True
	
	def nudge_right(self, auto_align=True):
		
		if not self._position_initiated:
			error("dish_commands.nudge_right() can't nudge without initiation")
		
		if self._nudge_left_count > 0:
			# to avoid positioning errors by nudging up and down
			error("dish_commands.nudge_right() cannot proceed, as azimuth has already nudged left since last absolute positioning")
		
		if self._nudge_right_count >= 4 and auto_align:
			debug("next nudge would be a full degree again, doing an absolute positioning instead")
			
			if self._position_azimuth >= MAXIMAL_AZIMUTH_INPUT:
				# azimut would overflow. Go to e.g. 0 instead
				
				self.goto_azimuth(MINIMAL_AZIMUTH_INPUT)
			else:
				self.goto_azimuth(self._position_azimuth + 1)
		
		else:
			self._position_azimuth_accurate = False
			self._dish.write("aznudge cw\r")
			# wait for motor to complete command
			sleep(NUDGE_MOTION_TIME_AZIMUTH)
			self._nudge_right_count += 1
	
	def nudge_left(self, auto_align=True):
		if not self._position_initiated:
			error("dish_commands.nudge_left() can't nudge without initiation")
		
		if self._nudge_right_count > 0:
			# to avoid positioning errors by nudging up and down
			error("dish_commands.nudge_left() cannot proceed, as azimuth has already nudged right since last absolute positioning")
		
		if self._nudge_left_count >= 4 and auto_align:
			debug("next nudge would be a full degree again, doing an absolute positioning instead")
			
			if self._position_azimuth <= MINIMAL_AZIMUTH_INPUT:
				# azimut would overflow. Go to e.g. 359 instead
				
				self.goto_azimuth(MAXIMAL_AZIMUTH_INPUT)
			else:
				self.goto_azimuth(self._position_azimuth - 1)
		
		else:
			self._position_azimuth_accurate = False
			self._dish.write("aznudge ccw\r")
			# wait for motor to complete command
			sleep(NUDGE_MOTION_TIME_AZIMUTH)
			self._nudge_left_count += 1
	
	def nudge_up(self, auto_align=True):
		if not self._position_initiated:
			error("dish_commands.nudge_up() can't nudge without initiation")
		
		if self._nudge_down_count > 0:
			# to avoid positioning errors by nudging up and down
			error("dish_commands.nudge_up() cannot proceed, as elevation has already nudged down since last absolute positioning")
		
		if self._position_elevation >= MAXIMAL_ELEVATION_INPUT:
			error("dish_commands.nudge_up() cannot increase elevation, as it has reached its maximum")
		
		if self._nudge_up_count >= 4 and auto_align:
			debug("next nudge would be a full degree again, doing an absolute positioning instead")
			
			self.goto_elevation(self._position_elevation + 1)
		else:
			self._position_elevation_accurate = False
			self._dish.write("elnudge up\r")
			# wait for motor to complete command
			sleep(NUDGE_MOTION_TIME_ELEVATION)
			self._nudge_up_count += 1
	
	def nudge_down(self, auto_align=True):
		if not self._position_initiated:
			error("dish_commands.nudge_down() can't nudge without initiation")
		
		if self._nudge_up_count > 0:
			# to avoid positioning errors by nudging up and down
			error("dish_commands.nudge_down() cannot proceed, as elevation has already nudged up since last absolute positioning")
		
		if self._position_elevation <= MINIMAL_ELEVATION_INPUT:
			error("dish_commands.nudge_down() cannot decrease elevation, as it has reached its minimum")
		
		if self._nudge_down_count >= 4 and auto_align:
			debug("next nudge would be a full degree again, doing an absolute positioning instead")
			
			self.goto_elevation(self._position_elevation - 1)
		
		else:
			self._position_elevation_accurate = False
			self._dish.write("elnudge down\r")
			# wait for motor to complete command
			sleep(NUDGE_MOTION_TIME_ELEVATION)
			self._nudge_down_count += 1
	
	def close_conn(self):
		self._dish.close()
