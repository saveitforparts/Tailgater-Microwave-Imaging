from serial import EIGHTBITS, PARITY_NONE, Serial, STOPBITS_ONE

from console_messages import error


class DishDevice:
	def __init__(self, device='/dev/ttyACM0', baud_rate=9600, parity=PARITY_NONE, stopbits=STOPBITS_ONE, bytesize=EIGHTBITS,
			serial_timeout=1):
		self.timeout = serial_timeout
		self.bytesize = bytesize
		self.stopbits = stopbits
		self.parity = parity
		self.device = device
		self.baud_rate = baud_rate
		
		self.dish_serial = None
	
	def init_serial(self):
		self.dish_serial = Serial(
			port=self.device, baudrate=self.baud_rate, bytesize=self.bytesize, parity=self.parity,
			stopbits=self.stopbits, timeout=self.timeout
			)
	
	def write(self, message: str):
		byte_message = bytes(message, 'utf-8')
		
		if self.dish_serial is None or not isinstance(self.dish_serial, Serial):
			error("Could not write message in serial_dish.write(): Serial not (yet) connected")
		
		for b in byte_message:
			self.dish_serial.write(b)
	
	def flush(self) -> None:
		
		if self.dish_serial is None or not isinstance(self.dish_serial, Serial):
			error("Could not flush in serial_dish.flush(): Serial not (yet) connected")
		
		self.dish_serial.flush()
	
	def reset_output_buffer(self) -> None:
		
		if self.dish_serial is None or not isinstance(self.dish_serial, Serial):
			error("Could not reset_output_buffer in serial_dish.reset_output_buffer(): Serial not (yet) connected")
		
		self.dish_serial.reset_output_buffer()
	
	def reset_input_buffer(self) -> None:
		
		if self.dish_serial is None or not isinstance(self.dish_serial, Serial):
			error("Could not reset_input_buffer in serial_dish.reset_input_buffer(): Serial not (yet) connected")
		
		self.dish_serial.reset_input_buffer()
	
	def read(self, size: int = 1) -> bytes | None:
		
		if self.dish_serial is None or not isinstance(self.dish_serial, Serial):
			error("Could not read in serial_dish.read(): Serial not (yet) connected")
		
		return self.dish_serial.read(size)
	
	def close(self) -> None:
		
		if self.dish_serial is None or not isinstance(self.dish_serial, Serial):
			error("Could not close in serial_dish.close(): Serial not (yet) connected")
		
		self.dish_serial.close()
