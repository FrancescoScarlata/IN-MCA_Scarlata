import argparse
import os.path
import sys
from pathlib import Path
#This should stay in the same place unmoved. Therefore it is called or from source or inside this folder.
#First case is when called inside the folder, the second when the current directory is source.
try:
	from hrFromX import hrFromX
except:
	from tests.hrFromX  import hrFromX

'''
	This file is made to test the hrv dynamic mode to read the video.
	This uses the hrv dynamic mode to calculate the bpm
'''

class hrFromDynHrv (hrFromX):
	'''
		Class that determines the hr with the green dynamic method
	'''
	def __init__(self,videoPath):
		super().__init__(videoPath, "hr dynHrv")	
		
	def importMethodScript(self):
		''' The method needed'''
		import HRV.HRVDynamicVideo as hrv
		self.hrv=hrv

	def determineHeartRate(self, showImages=False, showVideo=False, showArousal=False):
		''' Determine the health rate series but also the emotional state feature'''
		self.heartrate,self.feature=self.hrv.dynHrvElaboration(os.path.join(self.videoPath,self.videoName),showImages,showVideo, showArousal)

	def getEmotionalStateFeature(self):
		''' Returns the emotional state series'''
		return self.feature

if __name__=='__main__':
	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser(description='Write the name of the video (just the name.extension). It has to be in the right folder')

	ap.add_argument("-v", "--video", help="The name of the video.",required=True)
	
	args = vars(ap.parse_args())

	if args["video"] is not None:
	# check if the video input is correct
		hr=hrFromDynHrv(args["video"])
		if(hr.existsFile()):
			#print("[info hrFromDynGreen] File exists")
			#now that the file exists we can check for the file
			hr.determineHeartRate(True,True,True)
			heartrate= hr.getHeartRate()
			sf=hr.getEmotionalStateFeature()
			if(heartrate[-1][1]<0):
				print("the heartrate is certainly incorrect. There was an exception") 
			
			if(heartrate[-1][1]>0):
				print("[info "+os.path.basename(__file__)[:-3]+"] The heart rate should be "+ str(heartrate[-1][1]) )
				#for i in range (0,len(heartrate)):
				#	print("heart rate "+str(heartrate[i]))
				#	print("emotional feature normalized: "+str(sf[i][1]/sf[0][1]))
		else:
			print("[error "+os.path.basename(__file__)[:-3]+"] The file doesn't exist.")
	else:
		print("[error "+os.path.basename(__file__)[:-3]+"] No input given. Use 'python "+ os.path.basename(__file__) +" -h' to know what to write")	