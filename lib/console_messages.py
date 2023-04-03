def error(message: str):
	print("Error: %s" % message)
	exit(1)


def warning(message: str):
	print("Warning: %s" % message)


def debug(message: str):
	global PRINT_DEBUG
	if PRINT_DEBUG:
		print("Debug: %s" % message)


def info(message: str):
	global PRINT_INFO
	if PRINT_INFO:
		print("Info: %s" % message)
