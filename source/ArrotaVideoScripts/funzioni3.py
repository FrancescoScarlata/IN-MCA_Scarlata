import numpy as np
from numpy import abs, append, arange, arctan2, argsort, array, concatenate, \
	cos, diag, dot, eye, float32, float64, loadtxt, matrix, multiply, ndarray, \
	newaxis, savetxt, sign, sin, sqrt, zeros
from numpy.linalg import eig, pinv
import math
import mdp

'''
	script taken from the Arrota project. 
	These are the functions used in the "approccio 3" script
'''


lastValue = -1
counter = 0
pca_bpms = list()
def PCAAlg(x, fps):
	global lastValue
	global counter
	global pca_bpms
	primo = True
	prova = -1
	x = np.transpose(x)
	#print("dopo x: " + str(x))
	y = mdp.pca(x)
	#print("pca: " + str(y))
	secondComponent = y[:,1]
	#print("second: " + str(secondComponent))
	freqs, pruned = searchFreqs(secondComponent, fps, len(secondComponent))
	prova, index = calcolaProssimaFreqSensata(freqs, pruned)
	#print("pca: " + str(prova))
	pca_bpms.append(prova)



def searchFreqs(data, fps, lenMeans):
	raw = np.fft.rfft(data)
	fft = np.abs(raw)
	freqs = float(fps) / lenMeans * np.arange(lenMeans / 2 + 1)
	freqs = 60. * freqs 
	idx = np.where((freqs > 50) & (freqs < 180))
	pruned = fft[idx]
	#idx2 = np.argmax(pruned)
	freqs = freqs[idx]
	return freqs, pruned
	#return freqs[idx2]


def calcolaProssimaFreqSensata(freqs, pruned):
	idx2 = np.argmax(pruned)
	return freqs[idx2], idx2


