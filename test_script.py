import numpy as np
import struct


unusedSlotTag = -pow(2,31)
dp = '/Volumes/Analysis/2016-02-17-5/data003/data003.neurons'
headerVals = 4 #number of values to read from header
header = np.empty(headerVals)
f = open(dp, 'rb')
for i in range(headerVals): header[i] = struct.unpack('>i', f.read(4))[0]
[fileVersion, headerSlots, nTicks, samplingFreq] = header

f.seek(152)

hs = int(headerSlots)
buffer = np.zeros((hs, 4))
for rii in range(hs):
	for cii in range(4):
		buffer[rii,cii] = struct.unpack('>i', f.read(4))[0]

cellIds = buffer[:,0]
channels = buffer[:,1]
#total number of cells (subtract 1 for lisp version)

if not sum(channels == unusedSlotTag):  #version 33 uses this method
	numCells = len(cellIds)
else: #version 32 and 100 uses this method for determined numCells
	numCells = min(min((channels == unusedSlotTag).nonzero())) - 1

print numCells

f.close()
