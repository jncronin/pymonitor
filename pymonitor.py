#!/usr/bin/env python3.1

from optparse import OptionParser
from daemon3x import daemon
import monitor
import send_thecus
import time

parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
parser.add_option("-p", "--port", action="store", type="string", dest="port",
		default="/dev/ttyS1", metavar="PORT", help="listen to AVR on PORT")
parser.add_option("-D", "--daemon", action="store_true", dest="daemon",
		default=False, help="daemonize")
parser.add_option("-d", action="store_true", dest="debug",
		default=False, help="debug")
parser.add_option("--pid-file", action="store", type="string", dest="pidfile",
		default="/tmp/pymonitor.pid", help="pid-file location")
parser.add_option("--raid-device", action="store", type="string", dest="rdev",
		help="RAID device to monitor (default is first listed in mdstat)")
parser.add_option("--stop", action="store_true", dest="stop",
		default=False, help="stop a running daemon")
opts, args = parser.parse_args()

def main_loop():
	while True:
		msg1 = time.strftime("%d-%b-%Y %H:%M:%S")

		raid_db = monitor.get_status()
		try:
			if opts.rdev is None:
				my_rdev = raid_db.values().__iter__().__next__()
			else:
				my_rdev = raid_db[opts.rdev]

			if my_rdev.status == "active":
				msg2 = "RAID: Healthy"
			else:
				msg2 = "RAID: " + my_rdev.status
		except:
			msg2 = "RAID: not found"

		if opts.debug == True:
			print(msg1)
			print(msg2)
			print()
		else:
			send_thecus.write_message(msg1 = msg1, msg2 = msg2,
					port = opts.port)

		time.sleep(1)

class MyDaemon(daemon):
	def run(self):
		main_loop()

if opts.daemon == True:
	d = MyDaemon(opts.pidfile)
	if opts.stop == True:
		d.stop()
	else:
		d.start()
else:
	main_loop()

