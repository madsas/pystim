import pystim as pys
from struct import *

fname = '/Volumes/Analysis/2016-02-17-5/data003/data003'
dr = pys.datarun(fname)
a,b = dr.load_neurons()

