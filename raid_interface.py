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
	
		raid_dict[entry.name] = entry

	return raid_dict

def get_text():
	raid_db = get_status()

	if len(raid_db) == 0:
		return []

	ret = []
	for name, rdev in raid_db.items():
		if len(raid_db) == 1:
			ret_name = "RAID"
		else:
			ret_name = name

		if rdev.status == "active":
			ret_status = "Healthy"
		else:
			ret_status = rdev.status

		ret.append(ret_name + ": " + ret_status)
	
	return ret

if __name__ == "__main__":
	print(get_text())

