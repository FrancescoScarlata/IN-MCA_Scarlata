import argparse
import os.path
import sys
from pathlib import Path

try:
	from hrFromXThread import hrFromXThread
except:
	from tests.hrFromXThread  import hrFromXThread

# to make this class become a thread
from threading import Thread
# to use time.sleep for waiting
import time

class hrFromGreenThread(hrFromXThread):
	'''
		This class is the one that calls the green class for the elaborations. 
		This will update a current heartrate every x secs
		
	'''
	
	def __init__(self, nameMethod,src=0):
		super().__init__(nameMethod,src)
		
	### Thread scripts
	
	def start(self):
		''' Starts the thread using the update method as target
			Also, it has to start the webcam Thread
		'''
		self.greenThread = self.green.GreenWebcamThread(self.src).start()
		print("Start thread")
		super().start()
		self.currentHR=0
		self.currentFPS=0
		self.waitingTime=1
		return self	
		
	def update(self):
		''' keep looping infinitely until the thread is stopped.
			TO DO: this should have the calling to the webcam script to update the current heartrate '''
		print("Update thread")
		while True:
			# if the thread variable stopped is true, stop the thread
			if self.stopped :
				print ("stopped: "+ str(self.stopped))
				return
			
			# otherwise, every 0.5 sec, call the script of the webcam to update the current heartrate
			#print("waiting time: "+str(self.waitingTime))
			
			#get the data we want
			self.currentHR=self.greenThread.bpm
			self.currentFPS=self.greenThread.fps
			
			print("hr:  %.2f" % self.currentHR)
			print("fps:  %.2f" % self.currentFPS)
			time.sleep(self.waitingTime)
	
	def stop(self):
		''' Method called to say that the thread should be stopped '''
		self.stopped = True
		self.greenThread.stop()
	
	def importMethodScript(self):
		''' Here goes the import of the method we want to use to determine the health reate'''
		import ArrotaVideoScripts.GreenWebcamThread as green
		self.green=green
	
	def locateVideoFolder(self):
		''' this will define the folder where the video will be relative to this script. 
			TO DO: this has to change.'''
		self.videoPath=os.path.join(str(Path(__file__).resolve().parents[2]),'video')
		#sys.path.append(self.videoPath)
		
	def locateSourceFolder(self):
		''' this will append the source to the path.'''
		sys.path.append(str(Path(__file__).resolve().parents[1]))

	def determineHeartRate(self):
		''' Determine the health rate series and return it'''
		pass

	def getHeartRate(self):
		return self.heartrate
		
		
'''
JUST FOR TESTING THE THREAD
'''		
if __name__=='__main__':

	hrThread = hrFromGreenThread("green webcam",0).start()
	time.sleep(.900)
	
	#print("hrThread")
	#print(hrThread)
	
	time.sleep(60)
	hrThread.stop()
	print("current hr: "+str(hrThread.currentHR))
	#print(hrThread.name)
	




