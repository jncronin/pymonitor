import shlex, subprocess, re

sensors_command = "/usr/bin/sensors"

temp_match = re.compile(r"temp.*\+([0-9.]*).*C.*\(.*sensor \= CPU diode")

def run_sensors(cmd):
	args = shlex.split(cmd)
	proc = subprocess.Popen(args, stdout=subprocess.PIPE)
	oput = proc.stdout.read().decode("utf-8")
	
	temp = temp_match.search(oput)

	try:
		return "TEMP: " + temp.groups(0)[0] + "C"
	except AttributeError:
		return "TEMP: error"

def get_sensors_info():
	return run_sensors(sensors_command)

def get_text():
	return [get_sensors_info()]

def get_update_freq():
	return 15

if __name__ == "__main__":
	print(get_sensors_info())

