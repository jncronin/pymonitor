import shlex, subprocess, re

ip_command = "/sbin/ip -o -f inet addr"

ip_match = re.compile(r"[0-9]*:\s*(\S*)\s*inet\s*([0-9.]*)")
temp_match = re.compile(r"temp.*\+([0-9.]*).*C.*\(.*sensor \= CPU diode")

def run_ip(cmd):
	args = shlex.split(cmd)
	proc = subprocess.Popen(args, stdout=subprocess.PIPE)
	oput = proc.stdout.read().decode("utf-8")
	
	ips = ip_match.findall(oput)

	ret = set()

	for ip in ips:
		try:
			ret.add(ip[0] + ": " + ip[1])
		except:
			pass

	return sorted(ret)

def get_ip_info():
	return run_ip(ip_command)

def get_text():
	return get_ip_info()

if __name__ == "__main__":
	print(get_ip_info())

