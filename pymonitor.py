#!/usr/bin/env python3.1

from optparse import OptionParser
from daemon3x import daemon
import monitor
import send_thecus
import time
import smartctl_interface
import apcaccess_interface
import sensors_interface

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
parser.add_option("-S", "--smartctl", action="store_true", dest="smartctl",
		default=False, help="use smartctl to query the states of the drives")
parser.add_option("--smartctl-delay", action="store", type="int", dest="smartctldelay", help="number of seconds before rechecking SMART status", default=60)
parser.add_option("-U", "--apcaccess", action="store_true", dest="apcaccess",
		default=False, help="use apcaccess to query the states of a ups")
parser.add_option("--apcaccess-delay", action="store", type="int", dest="apcaccessdelay", help="number of seconds before rechecking UPS status", default=15)
parser.add_option("-T", "--sensors", action="store_true", dest="sensors",
		default=False, help="use sensors to detect system temperature")
parser.add_option("--sensors-delay", action="store", type="int", dest="sensorsdelay", help="number of seconds before rechecking sensors status", default=16)

opts, args = parser.parse_args()

def main_loop():
	maintimer = 0

	smarttimer = 0
	apcaccesstimer = 0
	sensorstimer = 0

	next_info_count = 0
	md_info_count = next_info_count
	next_info_count += 1

	if(opts.smartctl):
		smartctl_info_count = next_info_count
		next_info_count += 1

	if(opts.apcaccess):
		apcaccess_info_count = next_info_count
		next_info_count += 1

	if(opts.sensors):
		sensors_info_count = next_info_count
		next_info_count += 1

	while True:
		msg1 = time.strftime("%d-%b-%Y %H:%M:%S")

		if(opts.smartctl and smarttimer == 0):
			raid_msg = smartctl_interface.get_smart_info()

		if(opts.apcaccess and apcaccesstimer == 0):
			apcaccess_msg = apcaccess_interface.get_apcaccess_info()

		if(opts.sensors and sensorstimer == 0):
			sensors_msg = sensors_interface.get_sensors_info()

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

		if(opts.smartctl and maintimer % next_info_count == smartctl_info_count):
			msg2 = raid_msg
		if(opts.apcaccess and maintimer % next_info_count == apcaccess_info_count):
			msg2 = apcaccess_msg

		if(opts.sensors and maintimer % next_info_count == sensors_info_count):
			msg2 = sensors_msg

		if opts.debug == True:
			print(msg1)
			print(msg2)
			print()
		else:
			send_thecus.write_message(msg1 = msg1, msg2 = msg2,
					port = opts.port)

		smarttimer += 1
		if(smarttimer == opts.smartctldelay):
			smarttimer = 0

		apcaccesstimer += 1
		if(apcaccesstimer == opts.apcaccessdelay):
			apcaccesstimer = 0

		sensorstimer += 1
		if(sensorstimer == opts.sensorsdelay):
			sensorstimer = 0

		maintimer += 1

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

