#!/usr/bin/env python3.1

import os, re, imp
from daemon3x import daemon
from optparse import OptionParser
import time
import send_thecus

# Options
parser = OptionParser("usage: %prog [options]", version="%prog 2.0")
parser.add_option("-p", "--port", action="store", type="string", dest="port",
		default="/dev/ttyS1", metavar="PORT", help="communicate with AVR on PORT")
parser.add_option("-D", "--daemon", action="store_true", dest="daemon",
		default=False, help="daemonize")
parser.add_option("-d", action="store_true", dest="debug",
		default=False, help="debug")
parser.add_option("--pid-file", action="store", type="string", dest="pidfile",
		default="/tmp/pymonitor.pid", help="pid-file location")
parser.add_option("--update-freq", action="store", type="int", dest="updatefreq",
		default=15, help="number of seconds before requesting modules to update their output")
opts, args = parser.parse_args()

get_text = "get_text"
get_update_freq = "get_update_freq"
default_update_freq = opts.updatefreq

# build a list of modules
# the stagger value causes module updates to be staggered
stagger = 0
mod_dir = os.path.dirname(os.path.realpath(__file__))
mods = []
for file in os.listdir(mod_dir):
	match = re.match(r"^(\S*)_interface.py$", file)
	if match:
		fname = os.path.join(mod_dir, file)
		mname = match.groups(0)[0]
		mod = imp.load_source(mname, fname)

		mod_desc = { "name": mname, "mod": mod }
		if get_text in dir(mod):
			mod_desc[get_text] = mod.get_text
		else:
			mod_desc[get_text] = None

		if get_update_freq in dir(mod):
			mod_desc[get_update_freq] = mod.get_update_freq()
		else:
			mod_desc[get_update_freq] = default_update_freq

		mod_desc[get_update_freq] = mod_desc[get_update_freq] + stagger
		stagger = stagger + 1

		mod_desc["text"] = None
		mod_desc["countdown"] = 0
		mods.append(mod_desc)

def main_loop():
	idx = 0
	sub_idx = 0

	while True:
		# run gettext for each required module
		for mod in mods:
			if mod["countdown"] == 0:
				if mod[get_text] != None:
					mod["text"] = mod[get_text]()
				else:
					mod["text"] = []
				mod["countdown"] = mod[get_update_freq]
			else:
				mod["countdown"] = mod["countdown"] - 1

		# build the time string
		msg1 = time.strftime("%d-%b-%Y %H:%M:%S")

		# if zero-length mods, blank second line
		if len(mods) == 0:
			msg2 = ""
		else:
			# See if we've exceeded the sub index
			while sub_idx >= len(mods[idx]["text"]) or mods[idx]["text"][sub_idx] == None:
				sub_idx = 0
				idx = idx + 1

				# See if we've exceeded the index
				if idx >= len(mods):
					idx = 0

			# Load the string
			msg2 = mods[idx]["text"][sub_idx]

			# Increment counter for next run
			sub_idx = sub_idx + 1

		## Display the messages
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
	d.start()
else:
	main_loop()

