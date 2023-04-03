from datetime import datetime as dt


def timestamp():
	return dt.now().replace(microsecond=0).isoformat(' ')
