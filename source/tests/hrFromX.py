import argparse
import os.path
import sys
from pathlib import Path

class hrFromX:
	'''
		This class is the father to all the hr From ... methods. 
		This is made to help the raise of new tests for new methods
	'''
	
	def __init__(self, videoName, nameMethod):
		self.videoName=videoName
		self.locateVideoFolder()
		self.locateSourceFolder()
		self.importMethodScript()
		self.heartrate=[]
		self.name=nameMethod

	def importMethodScript(self):
		''' Here goes the import of the method we want to use to determine the health reate'''
		pass
		
	def locateVideoFolder(self):
		''' this will define the folder where the video will be relative to this script. '''
		self.videoPath=os.path.join(str(Path(__file__).resolve().parents[2]),'video')
		#sys.path.append(self.videoPath)
		
	def locateSourceFolder(self):
		''' this will append the source to the path.'''
		sys.path.append(str(Path(__file__).resolve().parents[1]))

	def determineHeartRate(self):
		''' Determine the health rate series and return it'''
		pass

	def existsFile(self):
		''' return True if the file exists, False otherwise '''
		return os.path.exists(os.path.join(self.videoPath,self.videoName))

	def getHeartRate(self):
		return self.heartrate