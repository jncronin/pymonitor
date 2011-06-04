import shlex, subprocess

smart_ctl_command = "/usr/sbin/smartctl -q silent -H -d sat"

disks = "/var/disks/front_tray/0", "/var/disks/front_tray/1", "/var/disks/front_tray/2", "/var/disks/front_tray/3", "/var/disks/front_tray/4"

def run_smartctl(cmd):
	args = shlex.split(cmd)
	retcode = subprocess.call(args)

	if (retcode & 1 != 0):
		return " "
	elif(retcode & 8 != 0):
		return "f"
	elif(retcode & 64 != 0):
		return "F"
	elif(retcode == 0):
		return "O"
	else:
		return "X"

def get_smart_info():
	ret = "Disks: ["

	for disk in disks:
		cmd = smart_ctl_command + " " + disk
		ret += run_smartctl(cmd)
	
	return ret + "]"

if __name__ == "__main__":
	print(get_smart_info())

