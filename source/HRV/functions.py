import numpy as np
from numpy import append, dot, sqrt, vstack, mean, cumsum, interp, arange
from numpy.linalg import eig, pinv
import scipy
from scipy.signal import butter, lfilter, welch
from scipy.interpolate import splrep, splev
import matplotlib.pyplot as plt
import pandas as pd
import warnings


# functions used in the main script
def adjustList (means, times): 
	''' It shouldn't happen, but if the times are more than the means, then the first elements is taken and added to the list x times
		where x = len(times)-len(means)
		returns the adjusted list of means
	'''
	singleMean = means[0]
	for i in range(len(means),len(times)):
		means.append(singleMean)
	return means
	
def calc_remaining_time(max_samples, n_samples, fps):
	'''It calculates the remaining seconds given the max number of samples, the number of current samples and the fps'''
	diff = max_samples - n_samples
	return int(diff/fps) + 1	
	
def fps_elaboration(times):
	''' Calculates the overall average fps of the program (webcam only) '''
	fps = len(times) / (times[-1] - times[0])
	#print("times: "+str(times[-1])+ " - " +str(times[0]))
	print("[Info fps_elaboration] fps: "+ str(fps))
	return fps
	
def butter_bandpass(lowcut, highcut, fs, order=5):
	''' This is the Butterworth bandpass method called by the filter. This is a scipy method'''
	nyq = 0.5 * fs
	low = lowcut / nyq
	high = highcut / nyq
	b, a = butter(order, [low, high], btype='band')
	return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
	''' This is the Butterworth bandpass filter method. This is a scipy method
		The fs is the sample rate, the lowcut and the hightcut are the  desired cutoff frequencies
	'''
	b, a = butter_bandpass(lowcut, highcut, fs, order=order)
	y = lfilter(b, a, data)
	return y

def detrend(means):
	'''  Smoothness prior approach as in the paper appendix: 
		"An advanced detrending method with application to HRV analysis " 
			by Tarvainen, Ranta-aho and Karjaalainen
		adapted from matlab to python
	'''
	t=len(means)
	l=10				#lambda
	I= np.identity(t)
	D2= scipy.sparse.diags([1, -2, 1], [0,1,2],shape=(t-2,t)).toarray() # this works the better than the spdiags in python 
	mean_stat= (I-np.linalg.inv(I+l**2*(np.transpose(D2).dot(D2)))).dot(means)
	#print(mean_stat)
	return mean_stat
	
def preProcess(means, fps):
	'''
		This method will do all the prepocessing of the temporal traces after the zero-mean.
		The steps of pre-processing are explained in the paper defined in the summary of the rppGElaboration function.
	'''

	#1) detrend with smoothness prior approach (SPA)
	means= detrend(means)
	
	#2) butterworth band pass filter (frequencies of 0.7 and 3.5 hz)
	lowcut = 0.7
	highcut= 3.5
	order = 5 						# *probably to tune* - the order of the butterworth filter
	
	means= butter_bandpass_filter(means, lowcut, highcut, fps, order)

	return np.real(means)

def rPPGElaboration(redMeans, greenMeans, blueMeans, times, fps, isWebcam=True, isDyn=False, framecount=1, startFrame=1) :
	''' This function will elaborate the ppg signal given the RGB temporal traces, the times of the samples and the fps
		This function is given from the following article:
		"Remote heart rate variability for emotional state monitoring" 
			by Y. Benezeth, P. Li, R. Macwan, K. Nakamura, R. Gomez, F. Yang
	'''
		
	## uniform samples with even times
	#print("redMeans and times: "+str(len(redMeans))+" , "+ str(len(times)))
	even_times=list()
	
	if isWebcam:
		even_times = np.linspace(times[0], times[-1], len(redMeans))	# create a list of values long len(means) from the first to the last time, with even distance between each other
		interpolatedR = np.interp(even_times, times, redMeans)			# linear interpolation to interpolate the values that should be in the even times. 
		interpolatedG = np.interp(even_times, times, greenMeans)
		interpolatedB = np.interp(even_times, times, blueMeans)
	
	else: # here there is not times
		# list of values long len(means) but with times as framecount/fps (the total of the frame / the frame per second)
		# framecount is passed as input only for the video
		# no linear interpolation this time because no time is recorded so we assume evenly recorded frames- assumption to change eventually
		even_times = np.linspace(0, int(framecount/fps), len(redMeans)) 	
		interpolatedR = redMeans			
		interpolatedG = greenMeans
		interpolatedB = blueMeans
		if isDyn:
			even_times = np.linspace(int(startFrame/fps), int(framecount/fps), len(redMeans)) 	
	
	### Pre- processing
	# 1) the zero mean for the 3 elements
	rawR = interpolatedR - np.mean(interpolatedR)
	rawG = interpolatedG - np.mean(interpolatedG)
	rawB = interpolatedB - np.mean(interpolatedB)
	
	#print("Pre Green shape: "+str(rawG.shape))
	# 2) detrend and butterworth bandpass filter
	rawR= preProcess(rawR,fps)
	rawG= preProcess(rawG,fps)
	rawB= preProcess(rawB,fps)
	
	### rPPG signal S using CHROM method
		# calculation of X
	X= 3*rawR - 2*rawG
		# calculation of Y
	Y=(1.5*rawR)+rawG-(1.5*rawB)
	
	## calculation of alpha
		# calculation of the X's standard deviation (sX)
	meanX=np.mean(X)
		
	sX=sqrt((1/len(X))*sum( np.real(x-meanX)**2 for x in np.real(X)))
	#print("sX: "+ str(sX))

		# calculation of the Y's standard deviation (sY)
	meanY=np.mean(np.real(Y))
	sY=sqrt((1/len(Y))*sum( np.real(y-meanY)**2 for y in np.real(Y)))
	#print("sY: "+ str(sY))
		# a= sX/sY
	alpha= sX/sY		
	
	# Signal S (rPPG signal)
	S= X-alpha*Y
	
	return S, even_times
	
def peakDetection(S, isDataShowing=False):
	''' This should detect the peaks from a PPG signal. The algorithm is taken from the following article:
		"An Efficient and Automatic Systolic Peak Detection Algorithm for Photoplethysmographic Signals" 
			by S. Kuntamalla and L. R. G. Reddy
	'''
	# the value that is the one that will change the number of peaks detected. 
	# Range is from 0 to 1. Higher means less peaks. 
	#Default is 0.7
	detectionPeakModifier=0.625
	
	#the 3-point moving average smoothing filter forward and backward direction	
	fwd= pd.Series(S).rolling(3, min_periods=1).mean()
	bwd= pd.Series(S[::-1]).rolling(3,min_periods=1).mean()
	movingAverage = vstack(( fwd, bwd[::-1] )) # lump fwd and bwd together
	movingAverage = mean( movingAverage, axis=0 ) # average	
	
	if(isDataShowing):
		plt.figure(3)
		plt.clf()	
		plt.plot(S, label= 'Signal')
		plt.plot(movingAverage, label='moving average') # the peaks of the ppg
		plt.legend(loc='best')
		plt.show()

	# Find all peaks and valleys in the signal Find the locations of peaks and valleys
	p=list() 
	pi=list()
	v=list()
	vi=list()
	
	for i in range(1,len(movingAverage)-1) :
		# peaks: P= S(n): s(n-1)<S(n)>S(n+1)
		if(movingAverage[i-1]<movingAverage[i] and movingAverage[i]>movingAverage[i+1]): # finds peaks and their locations
			p.append(movingAverage[i])
			pi.append(i)
		# Valleys: V= S(n): S(n-1)> S(n)<S(n+1)	
		if(movingAverage[i-1]>movingAverage[i] and movingAverage[i]<movingAverage[i+1]): # finds valleys and their locations
			v.append(movingAverage[i])
			vi.append(i)

	#check: if index of P[0] < index of V[0] -> discard peak value and location	
	if(pi[0]<vi[0]):
		del pi[0]
		del p[0]
		#print("[info peak detection]: deleting the first")
		
	if(len(pi)<len(vi)):
		del vi[-1]
		del v[-1]
	
	#print("len p e v after: " + str(len(p))+ " , " + str(len(v)) )
	
	vpd=list()
	#Calculate valleay to peak differences (VPD) =P(n)-V(n)
	for i in range( 0, len(p)):
		vpd.append(p[i]-v[i])
	
	secondInteration=0
	np=len(p)	#number of peaks
	
	#Loop: 
	while(secondInteration<2 and len(vpd)>1):
		
		elementsToDelete=list()
		# search VPD(n): with VPD(n) < 0.7*(VPD(n-1)+VPD(n)+VPD(n+1))/3
		# and Discard all P and locations for with VPD statisfies that condition
		for i in range(1,len(vpd)-1):
				if(vpd[i]< detectionPeakModifier*(vpd[i-1]+vpd[i]+vpd[i+1])/3): 		# if it satifies the condition has to eliminate the peak
					#print("i: "+str(i)+" and len pi: "+str(len(pi))+" also len vpd: "+str(len(vpd))) 
					elementsToDelete.append(i)			# save the index of the peaks to delete
					
		for i in range(len(elementsToDelete)-1,0,-1):
			#print("i: "+str(i)+" and len pi: "+str(len(pi)))
			del pi[elementsToDelete[i]]									# delete both valleys and peaks (in pairs i think)
			del p[elementsToDelete[i]]
			del vi[elementsToDelete[i]]
			del v[elementsToDelete[i]]
		
		# if NP is the same for 2 successive iteraction thant those are the true peaks and locations
		if(np==len(p)):
			secondInteration+=1
		else:
			secondInteration=0
			np=len(p)				#Current number of peaks (NP)
		
		#ReCalculate valley to peak differences (VPD) =P(n)-V(n)
		vpd.clear()
		for i in range( 0, len(p)):
			vpd.append(p[i]-v[i])		
	
	return pi	

def rHRVElaboration(S, times):
	'''
		This method will check the peaks of the rPPG signal, 
		and than it will calculate the time between the Peaks
	'''
	# detect peaks in the rPPG to calculate the hHRV
	peaks=peakDetection(S)
	
	#detect the RRI distance
	hrvSignal=list()
	for i in range (0,len(peaks)-1):
		hrvSignal.append(times[peaks[i+1]]-times[peaks[i]]) # time of the intervals
	
	
	#calculate the HRV temporal series - it's the intervals, so it should be this one
	return peaks, hrvSignal

def meanBeatPerMinute(ibi):
	'''
	This method, given the inter-beat intervals (ibi), will:
	- determine the mean ibi 
	- determine the heart rate from the mean ibi
	'''
	
	meanibi=np.mean(ibi)
	
	# how many time the mean stays in 60 secs
	hr= 60/meanibi
	return hr


def heartRateWithFreqs(rPPG,fps):
	'''
		This is an approach to take the heart rate from the frequencies of the intervals.
		Taken from the Arrota project
	'''
	raw = np.fft.rfft(rPPG)
	fft = np.abs(raw)			# ottengo l'amplitude spectrum
	freqs = float(fps) / len(rPPG) * np.arange(len(rPPG) / 2 + 1)
	freqs = 60. * freqs 			# passo ai bpm
	idx = np.where((freqs > 50) & (freqs < 180))
	
	pfreq = freqs[idx]
	freqs = pfreq			# freqs contiene frequenze cardiache nel range accettabile
	
	pruned = fft[idx]		# pruned contiene i valori fft associati a frequenze cardiache accettabili
	idx2 = np.argmax(pruned)	# ritorna l'indice del massimo valore di pruned, quindi avrò l'indice che corrisponde alla frequenza cardiaca accettabile nel range 51-179 bpm
	bpm = freqs[idx2]			# prendo la frequenza cardiaca
	
	x= np.linspace(0, fps/2, len(fft))*60.
	
	plt.figure(4)
	plt.clf()	
	plt.title('amplitude spectrum when finding the hr from highest peak frequencies')
	
	plt.plot(x, fft, label= 'amplitude')
	plt.grid(True)
	plt.xlabel('frequencies')
	plt.ylabel('fft')
	plt.legend(loc='best')
	plt.xlim(xmax=180)
	plt.show()
	print("freq bpm: "+str(bpm))
	return bpm
	
	
	
def hrElaboration(red,green,blue, times,fps,isDataShowing=False, isWebcam=True, isDyn=False, framecount=1, startFrame=1, showArousal=False):
	'''
		This function will:
		- Take the means of the components, the times and the last fps
		- the uniform samples and determine the ppg Signal
		- determine the peaks of the signal
		- determine the hrv
		- determine the heart rate from the hrv
	'''
	S,even_times = rPPGElaboration(red,green,blue, times,fps, isWebcam, isDyn, framecount, startFrame)		#the rPPG signal
	peaks, rHRVSignal = rHRVElaboration(S,even_times)
	
	if(isDataShowing):	# if you want to see here for each calculation, put it to True instead of using the variable
		heartRateWithFreqs(S,fps)
	
	#try: # frequency approach, but doesn't work good
		#print("with freq " +str(heartRateWithFreqs(rHRVSignal,fps)))
	#except:
		#print("[exception!: invalid freqs")
	if(showArousal):
		
		try:
			f,psd=determineHRVPeriodogram(rHRVSignal,fps) # calculate the periodogram
			stateFeature=determineTheFreqRatios(f,psd)	# returns the (vlf+lf)/hf value
		except:
			stateFeature=np.nan
	else:
		stateFeature=np.nan #  they will not be shown, so it's useless to determine it
	
	if(isDataShowing):
		#figure 1: the ppg signal + peaks
		#print("lengths. even and raw: "+ str(len(even_times)) +" ,  "+ str(len(S)))
		plt.figure(1)
		plt.clf()	
		plt.title('Graphic with the rPPG signal and the peaks')
		plt.plot(even_times, S, label= 'S')
		plt.plot(even_times[peaks],S[peaks], label='peaks', marker="o", ls="", ms=3 ) # the peaks of the ppg
		plt.grid(True)
		plt.xlabel('time(seconds)')
		plt.ylabel('signal')
		plt.legend(loc='best')

		# figure 2: the hrv signal
		#print("lengths. even and raw: "+ str(len(even_times[peaks])) +" ,  "+ str(len(hrvSignal)))
		plt.figure(2)
		plt.clf()
		plt.title('Graphic with the rHRV signal')
		plt.plot(even_times[peaks[:-1]], rHRVSignal, label= 'hrv')
		plt.grid(True)
		plt.xlabel('time(seconds)')
		plt.ylabel('time (hrv)')
		plt.legend(loc='best')
		
		if(showArousal):
			plt.figure(3)
			# figure 3: the periodogram of the hrv signal
			plt.clf()
			plt.title('Periodogram and the vlf (green), lf (yellow) and hf (red) ranges')
			plt.semilogy(f, psd)
			plt.axvline(x=0.04, color='green')
			plt.axvline(x=0.15, color='yellow')
			plt.axvline(x=0.4, color='red')
			plt.xlabel('frequency [Hz]')
			plt.ylabel('PSD [V**2/Hz]')		
			plt.ylim(ymin=10**-2)
			plt.legend(loc='best')
		
		plt.show()
	
	return meanBeatPerMinute(rHRVSignal), stateFeature
	
def determineHRVPeriodogram(rSignal, fs):
	'''
		periodogram is determined as shown in the python doc about the periodogram.
		It will take the rppg signal and the frame rate and return the frequency and the psd
		Found the passage from rri to PSD in the following page: 
		https://rhenanbartels.wordpress.com/2014/04/06/first-post/
	'''
	warnings.simplefilter("ignore", UserWarning)
	#Create time array
	# Divide by 1000.0 if RRi are in miliseconds.
	t = cumsum(rSignal)
	#Force the time array to start from zero.
	t -= t[0]

	#Create evenly spaced time array (4Hz).
	#After the creation of a evenly spaced time array, we are able to interpolate the RRi signal.
	tx = arange(t[0], t[-1], 1.0 / 4.0)
	tck = splrep(t, rSignal, s=0.0)
	rrix = splev(tx, tck, der=0)
	# determinate the periodogram
	Fxx, Pxx = welch(x=rrix, fs=4.0, window="hanning", detrend="linear")
	return Fxx, Pxx

def determineTheFreqRatios(Fxx,Pxx):
	''' Calcultates the value of (vlf+lf)/hf '''
	vlf,lf,hf=psdauc(Fxx,Pxx)
	#print ("\n the f. vl, l and h: "+str(vlf)+", "+ str(lf)+", "+str(hf) +"\n")	
	# calculate the ratio (vlf+lf)/hf
	ratio=(vlf+lf)/hf
	#print("ratio (vlf+lf)/hf: "+str(ratio)+"\n")
	return ratio	
	
def psdauc(Fxx, Pxx, vlf=0.04, lf = 0.15, hf = 0.4):
	'''
		Method taken in the following link: 
		https://rhenanbartels.wordpress.com/2014/04/06/first-post/
		This calculates the vlf, lf and hf from the periodogram
	'''
	df = Fxx[1] - Fxx[0]
	vl=0
	l=0
	h=0
	for i in range (0, len(Fxx)):
		# calculate the vlf. Interval 0<x<0.04 hz
		if(Fxx[i]<=vlf):
			vl+=Pxx[i]
		# calculate the lf. Interval 0.04<x< 0.15 hz
		if(Fxx[i]>=vlf and Fxx[i]<=lf):
			l+=Pxx[i]
		# calculathe te hf	Interval 0.15 <x< 0.4 hz
		if(Fxx[i]>=lf and Fxx[i]<=hf):
			h+=Pxx[i]
	return vl*df, l*df, h*df

	
def plotHRAndArousal(timesH,timesA, hr, arousal):
	'''Plots the hr series and the arousal series taking the times of the correspondent series'''
	plt.figure(4)
	# figure 3: arousal & hr
	plt.clf()
	plt.plot(timesH, hr, label= 'hr')
	plt.plot(timesA, arousal, label= 'arousal')
	plt.grid(True)
	plt.xlabel('time(seconds)')
	plt.legend(loc='best')
	plt.show()
	
	
	
	