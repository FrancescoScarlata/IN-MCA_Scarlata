import argparse
import os.path
import sys
from pathlib import Path

# to make this class become a thread
from threading import Thread
# to use time.sleep for waiting
import time

class hrFromXThread:
	'''
		This class is the father to all the hr From ... methods. 
		This is made to help the raise of new tests for new methods.
		
	'''
	
	def __init__(self, nameMethod,src=0):
		#self.locateVideoFolder()
		
		self.locateSourceFolder()
		self.importMethodScript()
		self.heartrate=[]
		self.name=nameMethod
		self.waitingTime=.5
		self.src=src
		
		self.stopped=False
		
	### Thread scripts
	
	def start(self):
		''' Starts the thread using the update method as target'''
		self.t = Thread(target=self.update, args=())
		self.t.daemon = True
		self.t.start()
		return self	
		
	def update(self):
		''' keep looping infinitely until the thread is stopped.
			TO DO: this should have the calling to the webcam script to update the current heartrate '''
		while True:
			# if the thread variable stopped is true, stop the thread
			if self.stopped :
				print ("stopped: "+ str(self.stopped))
				return
			
			# otherwise, every 0.5 sec, call the script of the webcam to update the current heartrate
			print("waiting time: "+str(self.waitingTime))
			
			#do something here
			
			
			
			print("hello update in hrFromXThread")
			time.sleep(self.waitingTime)
	
	def stop(self):
		''' Method called to say that the thread should be stopped '''
		self.stopped = True	
	
	def importMethodScript(self):
		''' Here goes the import of the method we want to use to determine the health reate'''
		pass	
	
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

	hrThread = hrFromXThread("name video").start()
	time.sleep(.900)
	
	print("hrFromXThread")
	print(hrThread)
	
	
	
	print(hrThread.name)
	time.sleep(2)
	hrThread.stop()




