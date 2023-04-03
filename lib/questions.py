from console_messages import warning


def get_valid_int(description: str, default: int, minimum: int, maximum: int) -> int:
	value = input("Enter %s (%i-%i; default %i): " % (description, minimum, maximum, default))
	try:
		value = int(value)
	except ValueError:
		value = default
	
	if type(value) != int:
		return default
	elif value > maximum:
		warning("Entered '%s' was too large, using maximal allowed value (%i)." % (description, maximum))
		return maximum
	elif value < minimum:
		warning("Entered '%s' was too small, using minimal allowed value (%i)." % (description, minimum))
		return maximum
	return value
