import struct

"""
This is a set of functions made to replace Java io functions for reading Vision output
"""

#globals

#functions

def readint(f):
	return struct.unpack('>i', f.read(4))[0]

def read_ei_file(fname):
	f = open(fname, 'rb')
	nlpoints = readint(f)
	nrpoints = readint(f)
	arrayID = readint(f)
	f.close()
	return nlpoints, nrpoints, arrayID
	
