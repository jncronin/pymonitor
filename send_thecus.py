import struct
import sys

write_string_msg = 0x11

def send(msg_code, msg, port = '/dev/ttyS1', msg_id = 1):
	fd = open(port, 'wb')
	
	new_msg = bytearray([msg_code])
	new_msg.extend(msg)
	
	fd.write(struct.pack('>ccH%dsc' % len(new_msg), '\x02', '\x01',
		len(new_msg), new_msg, '\x03'))

	fd.close()

def write_message(msg1, msg2, port = '/dev/ttyS1', msg_id = 1):
	str_msg = '{0:40.40}{1:20.20}'.format(msg1, msg2)
	send(write_string_msg, str_msg.encode('ascii'), port, msg_id)

if __name__ == '__main__':
	try:
		msg1 = sys.argv[1]
	except Exception:
		msg1 = "Hello World"
	try:
		msg2 = sys.argv[2]
	except Exception:
		msg2 = ""

	try:
		write_message(msg1, msg2)
	except e as Exception:
		print(e)

