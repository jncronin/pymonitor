import re
import collections

raid_entry = collections.namedtuple("raid_entry", "name status level drives size dev_name")
drive_entry = collections.namedtuple("drive_entry", "block_name raid_drive model")

def get_status():
	fd = open("/proc/mdstat", "r")
	txt = fd.read()
	fd.close()

	raid_dict = dict()

	for device in re.findall(r"(md[0-9]*) : (\S+) (\S+) (.*?)\n\s+?(\d+)\s+?blocks", txt):
		entry = raid_entry(device[0], device[1], device[2], [],
				device[4], "/dev/%s" % device[0])
	
		for drive in re.findall(r"[\w\[\]]+", device[3]):
			src_res = re.search(r"(\w+?)\[(\d+)\]", drive)

			sys_fd = open("/sys/block/%s/device/model" % src_res.group(1), "r")
			entry.drives.append(drive_entry(src_res.group(1),
				src_res.group(2), sys_fd.readline().rstrip()))
			sys_fd.close

		raid_dict[entry.name] = entry

	return raid_dict

if __name__ == "__main__":
	print(get_status())

