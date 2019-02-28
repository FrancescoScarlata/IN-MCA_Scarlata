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

class hrFromGreenThreadCirc(hrFromXThread):
	'''
		This class is the one that calls the green class for the elaborations. 
		This will update a current heartrate every x secs
		
	'''
	
	def __init__(self,nameMethod, filePath, src=0, debug=False):
		self.debug=debug
		super().__init__(nameMethod,src)
		self.locateSourceFolder()
		self.importTextManager(filePath)
		
		
		
	### Thread scripts
	
	def start(self ):
		''' Starts the thread using the update method as target
			Also, it has to start the webcam Thread
		'''
		self.greenThread = self.green.GreenWebcamThreadCirc(self.src,self.debug).start()
		#print("Start thread")
		super().start()
		self.currentHR=0
		self.currentFPS=0
		self.waitingTime=1
		return self	
		
	def update(self):
		''' keep looping infinitely until the thread is stopped.
			TO DO: this should have the calling to the webcam script to update the current heartrate '''
		#print("Update thread")
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
			
			#print("hr:  %.2f" % self.currentHR)
			#print("fps:  %.2f" % self.currentFPS)
			
			self.textManager.write(str(int(self.currentHR))+","+str(int(self.currentFPS)))
			#Print to file
			
			time.sleep(self.waitingTime)
	
	def stop(self):
		''' Method called to say that the thread should be stopped '''
		self.stopped = True
		self.greenThread.stop()
	
	def importMethodScript(self):
		''' Here goes the import of the method we want to use to determine the health reate'''
		import ArrotaVideoScripts.GreenWebcamThreadCirc as green
		self.green=green
	
	def importTextManager(self,filePath):
		'''
			Method called to istanciate the start the manager
		'''
		from TextManager import TextManager
		self.textManager=TextManager(filePath)
	
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

	hrThread = hrFromGreenThreadCirc("green webcam",os.path.join(str(Path(__file__).resolve().parents[3]),"output.txt"),0,True).start()
	
	#time.sleep(.900)
	
	#print("hrThread")
	#print(hrThread)
	
	#Just to don't stop the play
	while(True):
		time.sleep(60)
	
	hrThread.stop()
	
	#print("current hr: "+str(hrThread.currentHR))
	#print(hrThread.name)
	




