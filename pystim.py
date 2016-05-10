from __future__ import division
import os
import array
import numpy as np
import struct

"""
This library/module/package deals with importing EI (as analyzed by Vision) and electrical stim data. 

"""

class datarun(object): 
	"""
	This class will produce an datarun object
	"""
	#Class-wide variables
	fsep = os.sep #in order to make this code work on all OS

	def __init__(self, dataPath):
		"""
		Initializes datarun object given path to Vision output folder, on visual stimulation data
		"""
		#Check that data path exists
		if dataPath.endswith(fsep): dirnam = fsep.join(dataPath.split(fsep)[:-2])
		else: dirnam = fsep.join(dataPath.split(fsep)[:-1])
		if not os.path.isdir(dirnam):  
			print('Error: parent directory given does not exist')
			return 0

		#Parameters------------------------------
		namDict = {'rrs_prefix' : dataPath , 'rrs_neurons_path' : dataPath + '.neurons' , 'rrs_params_path' : dataPath + '.params' , 'rrs_ei_path' : dataPath + '.ei' , 'rrs_sta_path' : '.sta' , 'rrs_globals_path' : dataPath + '.globals' , 'rrs_movie_path' : dataPath + '.movie' , 'rrs_cov_path' : dataPath + '.cov' , 'rrs_ncov_path' : dataPath + '.ncov' , 'rrs_wcov_path' : dataPath + '.wcov'}

		#Set names based on path
		for key in namDict.keys(): setattr(self, key, namDict[key])

	
	def load_neurons(self, neuronIds = []):
		"""
		Loads a .neurons file based on the path given above. Will report missing file.

		The optional argument, neuronIds, is a list of specific neuron IDs to extract information for. 
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
			return 0
	
		#Open file and read header------------------------------
		headerVals = 4 #number of values to read from header
		header = np.empty(headerVals)
		f = open(self.rrs_neurons_path, 'rb')
		for i in range(headerVals): header[i] = struct.unpack(long_type, f.read(4))[0]
		[fileVersion, headerSlots, nTicks, samplingFreq] = header

		#Check sampling frequency
		if samplingFreq != defaultSampFreq: 
			print('Incorrect sampling frequency. Did not load neurons')
			return 0

		#Check file version (NOT READING EXTRA PARAMETERS: contamination, min_spikes, remove_duplicates)
		if fileVersion == 32: #Very old Obvius version. Used in Java code
			numRecords = 1
			spikeTimeType = long_type
		elif fileVersion == 33: #Current Obvius version (unknown?)
			numRecords = struct.unpack(long_type, f.read(4))[0]
			spikeTimeType = long_type
		elif fileVersion == 100: #Dumitru's version used in Manual sorting
			numRecords = 1
			spikeTimeType = float_type
		else:
			print('Unknown File Version')
			return 0 

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
			return 0

		#delete buffervar
		del buffervar

		#Update user
		print('Examining ' + str(numCells) + ' cells (RRS v.' + str(fileVersion) +')')

		#Determine Neurons to Extract------------------------------

		#Neuron ID for triggers
		triggerId = cellIds[0]
		
		#Determine which to load based on argument
		if neuronIds: 
			if not set(neuronIds) < set(cellIds): #make sure neuron IDs exist
				print('Error: Could not find some neurons specified by user')
				return 0
			if not len(set(neuronIds)) == len(neuronIds):
				print('Error: Duplicate neurons requested')
				return 0
			neurons = triggerId + neuronIds
		else: #load all neurons 
			neurons = cellIds

		#Initialize Variables------------------------------
		spikes = []
		spikeCounts = np.zeros((numCells))
		neuronsExtracted = []

		#Load Spike Times------------------------------
		for rec in range(numRecords): #loop through number of records (different from 1 in version 33)
			for cell in range(numCells):

				#Number of spikes by cell
				sc = struct.unpack(long_type, f.read(4))[0]
				spikeCounts[cell] = sc
				
				#Get index (necessary for file I/O)
				try:
					indexx = list(neurons).index(cellIds[cell])
				except ValueError:
					f.seek(4*sc, 1)
					continue
				
				#Read spikes (if cell is in list of desired neurons)
				spikes.append([struct.unpack(long_type, f.read(4))[0] for s in range(sc)])
				neuronsExtracted.append(cellIds[cell])

		#Close file
		f.close()

		#check that extracted correct number of neurons
		if not len(neuronsExtracted) == len(neurons):
			print('Error: failed to load all request neurons')
			return 0

		#Clean up output------------------------------
		triggers = spikes[0] #extract triggers
		
		#find neurons that are not triggers or duplicates
		indices = [i for i in range(len(neurons)) if neurons[i] > 0]
		neurons = [neurons[i] for i in indices]
		spikes = [spikes[i] for i in indices]
		electrodes = np.zeros((len(indices)))

		#determine channels associated with neurons
		for i in range(len(neurons)):
			indexx = list(cellIds).index(neurons[i])
			electrodes[i] = channels[indexx]

		#convert samples into seconds for everything
		spikes = [np.array(spike)/samplingFreq for spike in spikes]
		triggers = np.array(triggers)/samplingFreq
		duration = nTicks/samplingFreq

		#Return output------------------------------
		extras = {'channels' : electrodes, 'cellIds' : neurons, 'triggers' : triggers, 'duration' : duration, 'neuronsExtracted' : neuronsExtracted}

		#update user
		print('Extracted ' +  str(len(spikes))  + ' cells.')

		#Update self
		self.spikes = spikes
		self.extras = extras

		return spikes, extras

	#def load_params(self, verbose = False):
		"""
		Parses values form params file and adds them to datarun object. 
		If verbose is set to True, then steps will be reported.
		"""
	def load_ei(self, cellSpecification, arrayType = [], zeroDisconnected = False):
		"""
		Loads EI
		"""
		
		


