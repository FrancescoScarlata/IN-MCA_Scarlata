import numpy as np
from numpy import abs, append, arange, arctan2, argsort, array, concatenate, \
	cos, diag, dot, eye, float32, float64, loadtxt, matrix, multiply, ndarray, \
	newaxis, savetxt, sign, sin, sqrt, zeros
from numpy.linalg import eig, pinv
import math

'''
	script taken from the Arrota project approach 1
	adapted to the video mode.
	Left the arrota comment in italian
'''

def bpm_elaboration(means, fps, times=None):

	
	if( not times  == None):	#used in webcam, otherwise times is not needed
		even_times=list()
		even_times = np.linspace(times[0], times[-1], len(means))
		means = np.interp(even_times, times, means)
		
	#when is it video, we don't have the real times of the frames, so we assume the time between them is the same
	
	interpolated = np.hamming(len(means)) * means 	# moltiplica i valori con la finestra di Hamming, che è una sorta di gaussiana che quindi accentua i valori centrali all'interno di means
	interpolated = interpolated - np.mean(interpolated)		# ad ognuno dei valori poi toglie il valor medio dei valori stessi
	#print("interpolated: " + str(interpolated))
	raw = np.fft.rfft(interpolated)							# trasformata di fourier discreta a una dimensione dei valori, così passo al dominio delle frequenze
	#print("raw: " + str(raw))

	fft = np.abs(raw)			# ottengo l'amplitude spectrum
	freqs = float(fps) / len(means) * np.arange(len(means) / 2 + 1)		# np.arrange in questo caso restituisce una lista di interi da 0 a len(means) / 2 + 1
	#print("freqs: " + str(freqs))

	freqs = 60. * freqs 			# passo ai bpm
	#print("freqs2: " + str(freqs))
	idx = np.where((freqs > 50) & (freqs < 180))		# prendo un range di frequenze cardiache accettabili

	pruned = fft[idx]		# pruned contiene i valori fft associati a frequenze cardiache accettabili
	fft = pruned
	
	pfreq = freqs[idx]
	freqs = pfreq			# freqs contiene frequenze cardiache nel range accettabile
	
	idx2 = np.argmax(pruned)	# ritorna l'indice del massimo valore di pruned, quindi avrò l'indice che corrisponde alla frequenza cardiaca accettabile nel range 51-179 bpm

	bpm = freqs[idx2]			# prendo la frequenza cardiaca
	return bpm

	
	
def adjustList (means, times): 
	''' It shouldn't happen, but if the times are more than the means, then the first elements is taken and added to the list x times
		where x = len(times)-len(means)
		returns the adjusted list of means
	'''
	singleMean = means[0]
	for i in range(len(means),len(times)):
		means.append(singleMean)
	return means
	
	
def fps_elaboration(times):
	''' Calculates the overall average fps of the program (webcam only) '''
	fps = len(times) / (times[-1] - times[0])
	#print("times: "+str(times[-1])+ " - " +str(times[0]))
	#print("[Info fps_elaboration] fps: "+ str(fps))
	return fps	