import argparse
import os.path
import sys
from pathlib import Path
import numpy as np
import math
import hrComparison as hrC

#the folder upper than source. in this case inmca_Scarlata, but in this way it can change without problem
parentPath=str(Path(__file__).resolve().parents[1])
#sys.path.append(parentPath)

from tests import hrFromDynHrv as dynHrv,hrFromDynGreen as dynGreen,hrFromDynPca as dynPca


def determineTheHRs(filePath):
	'''
		This function will call the dynamic hr of each hr script (green, pca and hrv) and calculate the bpm serie for each one of them
		It will return the bpm traces.
		Each of the element of the trace will have 2 elements: 0 the timestamp, 1 the bpm calculated in that time.
		This script depends on the hr series that need to be determined
	'''
	hrs=list()
	hrs.append(dynGreen.hrFromDynGreen(filePath))
	hrs.append(dynPca.hrFromDynPca(filePath))
	hrs.append(dynHrv.hrFromDynHrv(filePath))
	# determine the hr series in all methods
	for hr in hrs:
		hr.determineHeartRate()
	return hrs
 
def meanHrPerWindow(hrMeasurements, lenOfHrCalculations, intervalScale,timeWindow):
	'''
		This takes the hr measurements in input and the length of the list of bpm calculated.
		It creates a list of elements where the time approssimate 1 per second and the bpm is calculated as mean between the second i-1 and the second i
	'''
	index=0
	meanHr=list()
	value=np.nan
	for i in range (0,lenOfHrCalculations):
		for j in range (index, len(hrMeasurements)):
		#takes just the first element in the interval. No interpolation, so when there are no elements, takes the last one memorized
			if((i+1)*timeWindow*intervalScale<=hrMeasurements[j][0] and (i+2)*timeWindow*intervalScale>=hrMeasurements[j][0]):
				value=hrMeasurements[j][1]
				meanHr.append([(i+1)*timeWindow, value])
				index=j
				#print ("mean i: "+ str(meanHr[i]))
				break
			
	return meanHr


	
if __name__=='__main__':
	
	ap = argparse.ArgumentParser(description="Additial feature, like debug and saving of the means value")

	ap.add_argument("-d", "--debug", help="add this if you want to see the debug info",action= 'store_true')
	ap.add_argument("-s", "--save", help="add this if you want to save the means in the relative file",action= 'store_true')
	
	args = vars(ap.parse_args())
	debug= args["debug"]
	
	# Variables
	allHr=list()
	hrTruth=list()
	print()
	#Take both video input, csv files name and the scale of the interval
	videofile= hrC.giveCorrectFilename("Please enter the name of the video file: ",True)
	csvfile= hrC.giveCorrectFilename("Please enter the name of the csv file: ",False)
	intervalScale=int(input("Please write the scale of the timestamp calculated in the ground truth (the csv file). \n(i.e. if the ground truth hr values are taken in milliseconds write 1000, if are taken in seconds write 1 etc): "))
	print()
	# calculation with the video corrected
	allHr =determineTheHRs(videofile)
	
	# read the hr truth from the csv file
	hrTruth=hrC.readTheCsvFile(csvfile)

	# Calculate the mean of the hr Truth per second.
	# Instead of compare 1 element of the calculated element with 40 elements in the hr truth csv file		
	meanHrTruth=meanHrPerWindow(hrTruth, len(allHr[0].getHeartRate()),intervalScale,10) # for now 10 seconds is fixed, can be changed elsewhere
	
	if(debug):	# show the len
		print ("[debug "+os.path.basename(__file__)[:-3]+"] Mean truth len: "+str(len(meanHrTruth)))
		for hr in allHr:
			print ("[debug "+os.path.basename(__file__)[:-3]+"] mean "+hr.name+" len: "+str(len(hr.getHeartRate())))

	# pca has a problem: in the way that is implemented, there is not the first element and due to the thread, it may not have the last one.
	'''
	for i in range(0,len(hrPca)):
		print (hrPca[i])
	'''
	if(debug):
		print("\n hr truth approximated \n")
		for i in range(0,len(meanHrTruth)):
			print (meanHrTruth[i])
	
	# condition made for compatibility between the 2 sets
	# Calculate the min and the max distances
	minsNmaxs=list()
	if (len(allHr[0].getHeartRate()[1:])<=len(meanHrTruth[1:])):
		minsNmaxs.append(hrC.maxValueTruthVsCalculated(meanHrTruth[1:], allHr[0].getHeartRate()[1:]))
		minsNmaxs.append(hrC.maxValueTruthVsCalculated(meanHrTruth[1:], allHr[1].getHeartRate()))	#pca
		minsNmaxs.append(hrC.maxValueTruthVsCalculated(meanHrTruth[1:], allHr[2].getHeartRate()[1:]))
	else:
		minsNmaxs.append(hrC.maxValueTruthVsCalculated(meanHrTruth[1:], allHr[0].getHeartRate()[1:-1]))
		minsNmaxs.append(hrC.maxValueTruthVsCalculated(meanHrTruth[1:], allHr[1].getHeartRate()[:-1]))	#pca
		minsNmaxs.append(hrC.maxValueTruthVsCalculated(meanHrTruth[1:], allHr[2].getHeartRate()[1:-1]))
	
	# condition made for compatibility between the 2 sets
	#Calculate the mean difference of the series
	means=list()
	if (len(allHr[0].getHeartRate()[1:])<=len(meanHrTruth[1:])):
		means.append(hrC.meanDiffHtruthVsCalculated(meanHrTruth[1:],allHr[0].getHeartRate()[1:]))
		means.append(hrC.meanDiffHtruthVsCalculated(meanHrTruth[1:],allHr[1].getHeartRate()))
		means.append(hrC.meanDiffHtruthVsCalculated(meanHrTruth[1:],allHr[2].getHeartRate()[1:]))
	else:
		means.append(hrC.meanDiffHtruthVsCalculated(meanHrTruth[1:],allHr[0].getHeartRate()[1:-1]))
		means.append(hrC.meanDiffHtruthVsCalculated(meanHrTruth[1:],allHr[1].getHeartRate()[:-1]))
		means.append(hrC.meanDiffHtruthVsCalculated(meanHrTruth[1:],allHr[2].getHeartRate()[1:-1]))
	
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
	
	print(hrC.writeWhoIsTheMinMax(mins,True,["The "," has the serie with one element most near the real series: "], nameMethods))
	
	print(hrC.writeWhoIsTheMinMax(maxs,False,["The "," has the serie with one element most far from the real series: "], nameMethods))

	print(hrC.writeWhoIsTheMinMax(means,True,["The "," has the serie with the least difference from the real series: "], nameMethods))	
	
	if(debug): # this will show a graphic with the hr
		hrC.plotHrSeries(meanHrTruth,allHr)
		
	print()		#just to clear a bit
	if(args["save"]):
		resultName='resultsVideoHrDyn.csv'
		hrC.saveMeansOnFile(means, allHr,videofile,resultName)
		print()
	print ("[info "+os.path.basename(__file__)[:-3]+"] now the program is terminating \n")
		
