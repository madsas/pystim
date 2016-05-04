import os.path
import array
import numpy as np
"""
This library/module/package deals with importing EI (as analyzed by Vision) and electrical stim data. 

"""

class datarun(object): 
	"""
	This class will produce an datarun object
	"""
	def __init__(self, dataPath):
		"""
		Initializes datarun object given path to Vision output folder, on visual stimulation data
		"""
		#Parameters------------------------------
		namDict = {'rrs_prefix' : dataPath , 'rrs_neurons_path' : dataPath + '.neurons' , 'rrs_params_path' : dataPath + '.params' , 'rrs_ei_path' : dataPath + '.ei' , 'rrs_sta_path' : '.sta' , 'rrs_globals_path' : dataPath + '.globals' , 'rrs_movie_path' : dataPath + '.movie' , 'rrs_cov_path' : dataPath + '.cov' , 'rros_ncov_path' : dataPath + '.ncov' , 'rrs_wcov_path' : dataPath + '.wcov'}

		#Set names based on path
		for key in namDict.keys(): setattr(self, key, namDict[key])

	
	def load_neurons(self, neuronIDs = []):
		"""
		Loads a .neurons file based on the path given above. Will report missing file.

		The optional argument, neuronIDs, is a list of specific neuron IDs to extract information for. 
		Default in this case is to load all neurons.
		"""
		#Parameters------------------------------
		defaultSampFreq = 20000
		blankValue = -2
		endOfHeader = 152
		unusedSlotTag = -pow(2,31)
		#file types
		long_type = '>i'
		unsigned_long_type = '>I'
		double_type = '>d'

		#Check if file exists
		if not os.path.isfile(self.rrs_neurons_path): 
			print('Neurons file does not exist')
			return
	
		#Open file and read header------------------------------
		headerVals = 4 #number of values to read from header
		header = np.empty(headerVals)
		f = open(self.rrs_neurons_path, 'rb')
		for i in range(headerVals): header[i] = struct.unpack(long_type, f.read(4))[0]
		[fileVersion, headerSlots, nTicks, samplingFreq] = header

		#Check sampling frequency
		if samplingFreq != defaultSampFreq: 
			print('Incorrect sampling frequency. Did not load neurons')
			return

		#Check file version (NOT READING EXTRA PARAMETERS: contamination, min_spikes, remove_duplicates)
		if fileVersion == 32: #Very old Obvius version. Used in Java code
			numRecords = 1
			spikeTimeType = long_type
		elif fileVersion == 33: #Current Obvius version (unknown?)
			numRecords = struct.unpack(long_type, f.read(4))[0]
			spikeTimeType = long_type
		elif fileVersion == 100: #Dumitru's version used in Manual sorting
			numberRecords = 1
			spikeTimeType = float_type
		else:
			print('Unknown File Version')
			return

		#Skip through end of blank header
		f.seek(endOfHeader)

		#Cell ID Header Information------------------------------
		hs = int(headerSlots)
		buffervar = np.zeros((hs, 4))
		for rii in range(hs):
			for cii in range(4):
				buffervar[rii,cii] = struct.unpack(long_type, f.read(4))[0]

		cellIds = buffervar[:,0]
		channels = buffervar[:,1]

		#total number of cells (subtract 1 for lisp version)
		if not sum(channels == unusedSlotTag):  #version 33 uses this method
			numCells = len(cellIds)
		else: #version 32 and 100 uses this method for determined numCells
			numCells = min(min((channels == unusedSlotTag).nonzero())) - 1

		#remove unused slots (vast majority)
		cellIds = cellIds[:numCells]
		channels = channels[:numCells]
				
		#some channels are read as negative (why??)
		channels = np.abs(channels)

		#check first cell is trigger
		if channels[0]: 
			print('trigger not found')
			return

		#delete buffervar
		del buffervar

		#Update user
		print('Examining ' + numCells + ' cells (RRS v.' + fileVersion +')')


