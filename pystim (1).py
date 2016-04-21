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
		defSampFreq = 20000
		#file types
		long_type = '>i'
		u

		#Check if file exists
		if not os.path.isfile(self.rrs_neurons_path): 
			print('Neurons file does not exist')
			return
	
		#Open file and read header
		headerVals = 4 #number of values to read from header
		header = np.empty(header_vals)
		f = open(self.rrs_neurons_path, 'rb')
		for i in range(headerVals): header[i] = struct.unpack('>i', f.read(4))[0]
		[fileVersion, headerSlots, nTicks, samplingFreq] = header

		#Check sampling frequency
		if samplingFreq != defSampFreq: 
			print('Incorrect sampling frequency. Did not load neurons')
			return

		#Check file version

