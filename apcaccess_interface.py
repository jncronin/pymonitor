import shlex, subprocess, re

apcaccess_command = "/sbin/apcaccess"

apc_match_charge = re.compile(r".*BCHARGE  : (\S*)")
apc_match_status = re.compile(r".*STATUS   : (\S*)")

def run_apcaccess(cmd):
	args = shlex.split(cmd)
	proc = subprocess.Popen(args, stdout=subprocess.PIPE)
	oput = proc.stdout.read().decode("ascii")
	
	charge = apc_match_charge.search(oput)
	status = apc_match_status.search(oput)

	try:
		return "UPS: " + status.groups(0)[0] + " " + str(int(float(charge.groups(0)[0]))) + "%"
	except AttributeError:
		return "UPS: not found"

def get_apcaccess_info():
	return run_apcaccess(apcaccess_command)

if __name__ == "__main__":
	print(get_apcaccess_info())

