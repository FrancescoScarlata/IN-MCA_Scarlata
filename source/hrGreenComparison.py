import argparse
import os.path
import sys
from pathlib import Path
import numpy as np
import csvManager as manager
import math
import matplotlib.pyplot as plt
import time

#the folder upper than source. in this case inmca_Scarlata, but in this way it can change without problem
parentPath=str(Path(__file__).resolve().parents[1])
#sys.path.append(parentPath)

from tests import hrFromGreen as green,	\
					hrFromCirGreen as cirGreen, hrFromCirGreen30 as cirGreen30,hrFromCirGreen15 as cirGreen15 # tests

def giveCorrectFilename(stringToSay, isVideo):
	'''
		tries to take as imput the file name and repeat untile the file exists.
		Returns the file name correct
	'''
	fileNotCorrect=True
	while(fileNotCorrect):
		filename=input(stringToSay)
		if(isVideo):
			filename=os.path.join(parentPath,"video",filename)
		else:
			filename=os.path.join(parentPath,"csv",filename)
		#print("the complete path is: "+filename)
		if(os.path.exists(filename)):
			fileNotCorrect=False
		else:
			print("the name of the file is not correct or in the wrong position.\nThis is where your file should be: "+filename +"\n")
	return filename

def readTheCsvFile(filePath):
	'''
		This function will call the csvReader To read the file and have back the columns wanted
		It will return the traces of timestamp and hr (in floats)
	'''
	hrTruth = manager.readLines(filePath,['timestamp', 'hr'])
	for i in range(0,len(hrTruth)):
		hrTruth[i]= [float(hrTruth[i][0]),float(hrTruth[i][1])]
		#print(hrTruth[i])
	return hrTruth


def determineTheHRs(filePath):
	'''
		This function will call the hr of each hr script (green, pca and hrv) and calculate the bpm serie for each one of them
		It will return the bpm traces.
		Each of the element of the trace will have 2 elements: 0 the timestamp, 1 the bpm calculated in that time.
		This script depends on the hr series that need to be determined
	'''
	hrs=list()
	hrs.append(green.hrFromGreen(filePath))
	hrs.append(cirGreen15.hrFromCirGreen15(filePath))
	hrs.append(cirGreen30.hrFromCirGreen30(filePath))
	hrs.append(cirGreen.hrFromCirGreen(filePath))
	
	# determine the hr series in all methods
	for hr in hrs:
		hr.determineHeartRate()
	return hrs
 
def meanHrPerSecond(hrMeasurements, lenOfHrCalculations, intervalScale):
	'''
		This takes the hr measurements in input and the length of the list of bpm calculated.
		It creates a list of elements where the time approssimate 1 per second and the bpm is calculated as mean between the second i-1 and the second i
	'''
	index=0
	meanHr=list()
	'''
	times=list()
	means=list()
	for i in range(0,len(hrMeasurements)):
		times.append(hrMeasurements[i][0])
		means.append(hrMeasurements[i][1])

	even_times = np.linspace(1, lenOfHrCalculations, lenOfHrCalculations)
	interpolated = np.interp(even_times, times, means)
	
	
	for i in range(0,len(interpolated)):
		meanHr.append([even_times[i],interpolated[i]])
		print(meanHr[i])
		
	print("len meanHr new: "+str(len(meanHr)))
	'''
	value=np.nan
	for i in range (0,lenOfHrCalculations):
		for j in range (index, len(hrMeasurements)):
			#takes just the first element in the interval. No interpolation, so when there are no elements, takes the last one memorized
			if((i+1)*intervalScale<=hrMeasurements[j][0] and (i+2)*intervalScale>=hrMeasurements[j][0]): 
				value=hrMeasurements[j][1]
				meanHr.append([i+1, value])
				#print(meanHr[-1])
				index=j
				#print ("mean i: "+ str(meanHr[i]))
				break
				
	print("len meanHr: "+str(len(meanHr)))
	
	#for i in range(0,len(meanHr)):
		#print(meanHr[i])
	print("\n")
	return meanHr

def maxValueTruthVsCalculated(hrTruth,hrCalc):
	'''
		this compares the hr truth series with the hr calculated (in one of the ways).
		it will give the  max and min difference between the 2 series (This compare can change after to give other values)
	'''
	max=0
	min=200
	#with a dynamic window with just one frame, sometimes the calculation will give a "nan"
	#we ignore those elements
	#print(hrCalc[0][1])
	if(not math.isnan(hrCalc[0][1])):			
												
		max=np.abs(hrTruth[0][1]-hrCalc[0][1])
		min=max
	
	for i in range (1, len(hrTruth)):
		if(not math.isnan(hrCalc[i][1])):
			value=np.abs(hrTruth[i][1]-hrCalc[i][1])
			if(value<min):
				min=value
			if(value>max):
				max=value
	return min,max
	
def meanDiffHtruthVsCalculated(hrTruth,hrCalc):
	'''
		this compares the hr truth series with the hr calculated (in one of the ways).
		it will give the mean difference between the 2 series (This compare can change after to give other values)
	'''
	diff=list()
	for i in range (10, len(hrTruth)): #10 just to avoid the first 10 seconds because they will be surely wrong
		if((not math.isnan(hrCalc[i][1])) and (not math.isnan(hrTruth[i][1]))):
			diff.append(np.abs(hrTruth[i][1]-hrCalc[i][1]))	
	return np.mean(diff)
	
def writeWhoIsTheMinMax(values, isMin, commonStrings,specialStrings):
	'''
		It will check the min or max between some values and it will say something about it.
		It inputs are the following:
		- values: a list of elements (float or int) on which needs to be calculated the min or max
		- isMin: a boolean. True if it needs to calculate the min, False elsewhere
		- The common parts to say: i.e. 0= "The serie ", 1=" has the serie with the least with the real serie"
		- Special strings: these are the ones that are said between the element j and j+1 of the commonParts. i.e. 0="hr green", 1="hr pca" etc.
		A Full string example with 1 special string and 2 common strings is: 
			"The green hr has the serie with one element most far from the real series"
	'''
	if(isMin):
		valueToCompare= np.min(values)
	else :
		valueToCompare= max(values)
	for i in range(0, len(values)):
		if(valueToCompare==values[i]):
			stringToSend=str(commonStrings[0]+specialStrings[i])
			for j in range (1, len(commonStrings)):
				stringToSend+=str(commonStrings[j])
				if(len(values)*j<len(specialStrings)):
					stringToSend+=str(specialStrings[i+j*len(values)])
			stringToSend+="{:.2f}".format(valueToCompare)
			return stringToSend

def plotHrSeries(hrTruth, hrsCalc):
	''' this function will plot series made in a hrFrom- like way.
		In particular it will show the real hr series and the hr calculated
	'''
	plt.figure(1)
	# figure 1: hr Truth & hrs calculated
	plt.clf()
	plt.title('Graphic with all the hr calculated and the truth hr values')
	timesT=list()
	hrT=list()
	for row in hrTruth:
		timesT.append(row[0])
		hrT.append(row[1])

	plt.plot(timesT, hrT, label= 'truth hr')
	
	for hr in hrsCalc:
		timesC=list()
		hrC=list()
		for row in hr.getHeartRate():
			timesC.append(row[0])
			hrC.append(row[1])
	
		plt.plot(timesC, hrC, label= hr.name)
	
	plt.grid(True)
	plt.xlabel('time(seconds)')
	plt.ylabel('bpm (seconds)')
	plt.legend(loc='best')
	plt.show()
	
def resultExists(filename):
	''' checks if the result file exists '''
	if(os.path.exists(filename)):
		return True
	else:
		return False

def saveMeansOnFile(means, hrs,videofile,resultName):
	''' 
	This will create a csv file called resultsVideoHr.
	First checks if the video has not been calculted. If it is, just print that is has been already calculated
	The format will be the following:
		videofile, hr name method, mean distance
	Input:
		means and hrs have the same length
		hrs is a list of hr classes of the type "hrFrom..."
		
	For now the file is in source
	'''
	
	resultsExists=resultExists(resultName) # checks if there is the file
	if(resultsExists):
		if(manager.checkVideofileIsSaved(resultName,videofile)):
			print("video already calculated and added in the list")
			return
	
	names=list()
	for hr in hrs:
		names.append(hr.name)
	if(resultsExists):
		manager.writeMeanValues(resultName,videofile,names,means,True)	# calls the csv manager to save the data
	else:
		manager.writeMeanValues(resultName,videofile,names,means,False)	# calls the csv manager to save the data
	print("[info "+os.path.basename(__file__)[:-3]+"] means saved correctly")
	
	
			
if __name__=='__main__':
	
	ap = argparse.ArgumentParser(description="Additial feature, like debug and saving of the means value")

	ap.add_argument("-d", "--debug", help="add this if you want to see the debug info",action= 'store_true')
	ap.add_argument("-s", "--save", help="add this if you want to save the means in the relative file",action= 'store_true')
	args = vars(ap.parse_args())
	
	debug=args["debug"]
	
	# Variables
	allHr=list()
	hrTruth=list()
	print()
	#Take both video input, csv files name and the scale of the interval
	videofile= giveCorrectFilename("Please enter the name of the video file: ",True)
	csvfile= giveCorrectFilename("Please enter the name of the csv file: ",False)
	intervalScale=int(input("Please write the scale of the timestamp calculated in the ground truth (the csv file). \n(i.e. if the ground truth hr values are taken in milliseconds write 1000, if are taken in seconds write 1 etc): "))
	print()
	startC=time.clock()
	# calculation with the video corrected
	allHr =determineTheHRs(videofile)
	
	print("time to calculate: "+str(int(time.clock()-startC))+" seconds")
	
	# read the hr truth from the csv file
	hrTruth=readTheCsvFile(csvfile)

	# Calculate the mean of the hr Truth per second.
	# Instead of compare 1 element of the calculated element with 40 elements in the hr truth csv file		
	meanHrTruth=meanHrPerSecond(hrTruth, len(allHr[0].getHeartRate()),intervalScale)
	
	if(debug):	# show the len
		print ("[debug "+os.path.basename(__file__)[:-3]+"] Mean truth len: "+str(len(meanHrTruth)))
		for hr in allHr:
			print ("[debug "+os.path.basename(__file__)[:-3]+"] mean "+hr.name+" len: "+str(len(hr.getHeartRate())))
	# pca has a problem: in the way that is implemented, there is not the first element and due to the thread, it may not have the last one.
	
	'''
	for row in allHr[0].getHeartRate():
		print (row)
	'''
	'''
	print ("\n truth\n")
	for row in hrTruth:
		print (row)
	'''
	
	# condition made for compatibility between the 2 sets
	# Calculate the min and the max distances
	minsNmaxs=list()
	if (len(allHr[0].getHeartRate()[1:])<=len(meanHrTruth[1:])):
		minsNmaxs.append(maxValueTruthVsCalculated(meanHrTruth[1:], allHr[0].getHeartRate()[1:])) # green
		minsNmaxs.append(maxValueTruthVsCalculated(meanHrTruth[1:], allHr[1].getHeartRate()[1:])) # green 15
		minsNmaxs.append(maxValueTruthVsCalculated(meanHrTruth[1:], allHr[2].getHeartRate()[1:])) # green 30
		minsNmaxs.append(maxValueTruthVsCalculated(meanHrTruth[1:], allHr[3].getHeartRate()[1:])) # green 45
	else:
		minsNmaxs.append(maxValueTruthVsCalculated(meanHrTruth[1:], allHr[0].getHeartRate()[1:-1])) # green
		minsNmaxs.append(maxValueTruthVsCalculated(meanHrTruth[1:], allHr[1].getHeartRate()[1:-1]))	# green 15
		minsNmaxs.append(maxValueTruthVsCalculated(meanHrTruth[1:], allHr[2].getHeartRate()[1:-1])) # green 30
		minsNmaxs.append(maxValueTruthVsCalculated(meanHrTruth[1:], allHr[3].getHeartRate()[1:-1])) # green 45
		
	# condition made for compatibility between the 2 sets
	#Calculate the mean difference of the series
	means=list()
	if (len(allHr[0].getHeartRate()[1:])<=len(meanHrTruth[1:])):
		means.append(meanDiffHtruthVsCalculated(meanHrTruth[1:],allHr[0].getHeartRate()[1:])) 
		means.append(meanDiffHtruthVsCalculated(meanHrTruth[1:],allHr[1].getHeartRate()[1:]))
		means.append(meanDiffHtruthVsCalculated(meanHrTruth[1:],allHr[2].getHeartRate()[1:]))
		means.append(meanDiffHtruthVsCalculated(meanHrTruth[1:],allHr[3].getHeartRate()[1:]))
	else:
		means.append(meanDiffHtruthVsCalculated(meanHrTruth[1:],allHr[0].getHeartRate()[1:-1]))
		means.append(meanDiffHtruthVsCalculated(meanHrTruth[1:],allHr[1].getHeartRate()[1:-1]))
		means.append(meanDiffHtruthVsCalculated(meanHrTruth[1:],allHr[2].getHeartRate()[1:-1])) 
		means.append(meanDiffHtruthVsCalculated(meanHrTruth[1:],allHr[3].getHeartRate()[1:-1]))

	print() #just to clear a bit
	for i in range(0,len(allHr)):
		print ("[info "+os.path.basename(__file__)[:-3]+"] "+allHr[i].name+" mean distance from the truth hr series: "+"{:.2f}".format(means[i]))
	
	print("\n")		#just to clear a bit
	
	nameMethods=list()
	for hr in allHr:
		nameMethods.append(hr.name)
	
	mins=list()
	maxs=list()
	for min in minsNmaxs:
		mins.append(min[0])
		maxs.append(min[1])
	
	print(writeWhoIsTheMinMax(mins,True,["The "," is the serie with the most near element to the real series. The distance is: "], nameMethods))
	
	print(writeWhoIsTheMinMax(maxs,False,["The "," is the serie with the most far element from the real series. The distance is: "], nameMethods))

	print(writeWhoIsTheMinMax(means,True,["The "," is the serie with the least distance difference from the real series. The mean distance is: "], nameMethods))	
	
	if(debug):  # this will show a graphic with the hr
		plotHrSeries(meanHrTruth,allHr)
	
	print()		#just to clear a bit
	if(args["save"]):
		resultName='resultsVideoGreenHr.csv'
		saveMeansOnFile(means, allHr,videofile,resultName)
		print()		#just to clear a bit
	
	print ("[info "+os.path.basename(__file__)[:-3]+"] now the program is terminating \n")
		
