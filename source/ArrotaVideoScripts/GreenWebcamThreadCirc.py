import cv2
import numpy as np
import sys
import time
from pathlib import Path
import os.path
#This script will become a thread
from threading import Thread

from cameraUtils import WebcamStreamForHRV as web

try:
	from funzioni1 import bpm_elaboration, adjustList, fps_elaboration
except ImportError:
	from .funzioni1 import bpm_elaboration, adjustList, fps_elaboration

sourcePath=str(Path(__file__).resolve().parents[1])


class GreenWebcamThreadCirc:
	'''
		This class will manage the elaboration of the heartrate from webcam with the ica mode.
		This will start a thread, call the green elaboration and every 1 sec determine the heartrate	
		
	'''

	### - - - - - THREAD METHODS
	
	def __init__(self, src=0, debug=False):
		'''
		Constructor fo the GreenWebcam
		'''
		self.camSource=src
		# initialize the variable used to indicate if the thread should
		# be stopped
		self.stopped = False
		self.debug=debug;
		
		# Initializing all the variables
		self.vs = web.WebcamStreamForHRV(self.camSource).start() #to change when this becomes a function	
		self.face_cascade = cv2.CascadeClassifier(os.path.join(sourcePath,'haarcascade_frontalface_default.xml'))
	
		#variables
		self.frame_width = self.vs.getWidth()
		self.frame_height = self.vs.getHeight()
	
		self.redCol = (0, 0, 255) 		# red color in BGR
		self.greenCol= (0, 255, 0)		# green color in BGR
		self.tsize = 3					#Dimension of the time elements

		#To delete
		self.max_samples = 300			# number of frames to collect before end
		self.remaining = -1      		# const to say when it is the end
		self.t0=0
		self.bpm=0
		self.fps=0
	
		self.times = list()
		self.bpms= list()					# a series with the second in question and the bpm calculated for that second
		self.means = list()
	
		self.firstTime = True
		self.secondsBeforeNewLine=20	# cosmetic variable to set after how many second-points it should have a new line
		self.secondsInTheList= 40			# The seconds window to keep
		
		# variables to not calculate everytime
		self.leftOffset=				int(self.frame_width/21) 		# around 30 in offeset with 640 as frame width
		self.highHeightOffset=		int(self.frame_height* 3/24) 	# 60 in offeset with 480 as frame height
		self.lowHeightOffset=		int(self.frame_height* 21/24) 	# 420 in offeset with 480 as frame height
		self.heightOffsetSeconds=	int(self.frame_height* 5/24) 	# 100 in offeset with 480 as frame height
		self.timeBetweenCalculations=0 	#a variable to wait before recalculate the bpm
		
		self.foreheadY= 0	
		self.foreheadX= 0
		self.foreheadX2 = 0
		self.foreheadY2 = 0
		
		
		
		print("starting the green webcam mode circular...")
		#print("please wait while it is calculating:")
		

	def start(self):
		# start the thread to read frames from the video stream
		self.t = Thread(target=self.update, args=())
		self.t.daemon = True
		self.t.start()
		return self

	def update(self):
		# keep looping infinitely until the thread is stopped
		while True:
			# if the thread indicator variable is set, stop the thread
			#print("self.stopped in green web: "+str(self.stopped))
			if self.stopped :
				#print ("stop: "+ str(self.stopped))
				#print("[info] the last calculated bpm is : " + str(self.bpm))
				
				return
				
			# otherwise, read the next frame from the stream
			#here the greenElaboration
			self.greenElaboration()
		
	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True
		self.vs.stopSaving()
		# do a bit of cleanup
		self.vs.stop()
		cv2.destroyAllWindows() 
		#print("greenwebcam should stop")
	
	
	
	
	### - - - Classic methods

	def determineMeans(self,vs,green,oldTimes, x1, y1, x2, y2):
		'''
		This function is called for make the mean frames.
		It will:
		- call the webcam stream to get the frames and times
		- determine the means 
		- return the lists
		'''
		frames, times = vs.getFramesAndTime() # reads from the vs
		#It will add the mean of just the new ones
		for i in range(0,len(frames)): # frames in rgb. the frame is BGR
			green.append(np.mean(frames[i][y1:y2,x1:x2,1]))
			oldTimes.append(times[i])

		return green, oldTimes
	
	
	def greenElaboration(self):
		'''
		Script adapted from the arrota project. It uses the ica mode to calculate the bpm series.
		In this case, this all happens each frame instead of the usual loop while inside this method
		'''

		self.frame = self.vs.read()
		if time.clock() > 3:    		# skip the first seconds to setup the focus of the camera

			#Face detection
			gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
			faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

			if len(faces) == 1: 		#The detection is of just 1 face 
				if self.debug==True:
					cv2.putText(self.frame, "Please, don't move", (self.leftOffset, self.lowHeightOffset), cv2.FONT_HERSHEY_SIMPLEX, self.tsize-2, self.redCol, 1, cv2.LINE_AA)  # just a warning
				for (x,y,w,h) in faces:
					#Skin detection of the foreground
					reducedWidth = int(w * 0.63)
					modifiedX = int(w * 0.15)
					reduceHeigh = int(h * 0.25)
					inizioY = int(h * 0.1)
					frontX = int(w - reducedWidth)
					
					# Picking the coordinates of the forehead
					self.foreheadY = y+inizioY	
					self.foreheadX = x+frontX
					self.foreheadX2 = x+reducedWidth
					self.foreheadY2 = y+reduceHeigh
					
					# initial time and start the savings
					if self.firstTime:
						self.firstTime = False
						self.t0 = time.clock()			
						self.vs.startSaving()	
					# Note: put it down when it determines the foreground to pass
					#cv2.rectangle(frame, (foreheadX, foreheadY), (foreheadX2, foreheadY2), greenCol, 2) # the rectangle that will shown on the forehead
			else:
				
				if len(faces) == 0:
					#print("[info] Green WebcamThreadCirc: no face detected")
					if self.debug==True: 
						cv2.putText(self.frame, "No face detected...", (self.leftOffset, self.lowHeightOffset), cv2.FONT_HERSHEY_SIMPLEX, 1, self.redCol)
				else:
					#print("[info] Green WebcamThreadCirc: too many facec detected")
					if self.debug==True: 
						cv2.putText(self.frame, "Too many faces...", (self.leftOffset, self.lowHeightOffset), cv2.FONT_HERSHEY_SIMPLEX, 1, self.redCol)
					
			if len(self.times) > 9 and len(self.means)>0:      # wait some frames before to start the calculations of the bpm
				#	The CALCULATION
				# calculates for each second more or less, because the user won't understand the difference between time+0.5 or time +1 seconds 
				if time.clock()-self.timeBetweenCalculations>= 1 :			
					self.timeBetweenCalculations=time.clock()
					 
					# determines the means for the new frames
					if(not self.vs.isNotSaving):
						# TO DO: circular means/greens
						if( len(self.bpms)>=self.secondsInTheList):
							del self.bpms[0]
							del self.means[0:int(self.fps)]
							del self.times[0:int(self.fps)]
							
						self.means,self.times = self.determineMeans(self.vs,self.means, self.times,self.foreheadX, self.foreheadY, self.foreheadX2, self.foreheadY2 )
						if self.debug==True: 
							cv2.rectangle(self.frame, (self.foreheadX, self.foreheadY), (self.foreheadX2, self.foreheadY2), self.greenCol, 2) # the rectangle that will be shown on the forehead
					#print("After determine red : "+str(len(red_means))+ "and times: "+str(len(times)))
					
					if not len(self.times) == len(self.means): 					# when the two lenghts are different, for some reasons
						print("[info check len(times) != len(red_means)] different len: "+str(len(self.times))+" , "+ str(len(self.means)))
						self.means = adjustList(self.means, self.times)
					self.fps = fps_elaboration(self.times)

					self.bpm=bpm_elaboration(self.means, self.fps,self.times)
					self.bpms.append([time.clock()-self.t0, int(self.bpm)])
					# this works for when there is a time window to investigate. 30 is for 30 seconds
					
					if(self.fps*30>250):
						max_samples=int(self.fps)*30
				else:
					#TO DO: 35 is static. we should need a proportion time
					self.fremaining = int(35+self.t0-time.clock()) 	#probably to change with a dynamic remaining
					#print("time passed after the last check: "+ str(timeBetweenCalculations))
					
				if(self.bpm>0):	# In this way we won't show non positive bpm (the start or wrong calculations)
					if self.debug==True: 
						cv2.putText(self.frame, "bpm: " + str(int(self.bpm)), (self.foreheadX-25, self.foreheadY-45), cv2.FONT_HERSHEY_SIMPLEX, self.tsize-2, self.redCol) # display the bpm	
			else:
				if self.debug==True: 
					cv2.putText(self.frame, "Starting...", (self.leftOffset, self.highHeightOffset), cv2.FONT_HERSHEY_SIMPLEX, 1, self.redCol)	# second message
					cv2.putText(self.frame, "Please, don't move", (self.leftOffset, self.lowHeightOffset+40), cv2.FONT_HERSHEY_SIMPLEX, self.tsize-2, self.redCol, 1, cv2.LINE_AA) # just a warning
				
				if time.clock()-self.timeBetweenCalculations>= 1 :			# i'm trying to calculate not for each frame but for each second more or less, to increase the fps
					self.timeBetweenCalculations=time.clock()
					# determines the means for the new frames
					if(not self.vs.isNotSaving):
						self.means,self.times= self.determineMeans(self.vs,self.means, self.times, self.foreheadX, self.foreheadY, self.foreheadX2, self.foreheadY2)
						if self.debug==True: 
							cv2.rectangle(self.frame, (self.foreheadX, self.foreheadY), (self.foreheadX2, self.foreheadY2), self.greenCol, 2) # the rectangle that will be shown on the forehead
					if self.debug==True: 
						cv2.imshow('Webcam', self.frame)
				
		else:
			if self.debug==True: 
				cv2.putText(self.frame, "Loading...", (self.leftOffset, self.highHeightOffset), cv2.FONT_HERSHEY_SIMPLEX, self.tsize-2, self.redCol) # first message
				cv2.putText(self.frame, "Please, take off your glasses", (self.leftOffset, self.lowHeightOffset), cv2.FONT_HERSHEY_SIMPLEX, self.tsize-2, self.redCol, 1, cv2.LINE_AA) # just a warning
				#cv2.imshow('Webcam', frame)

		'''	
		if time.clock() >= 180:	# this is ok only if the time of invastigation is under the 180 seconds
			print("[Debug time clock>180] over the time break")
			self.vs.stop()
			cv2.destroyAllWindows()
			return -3
		'''

		if self.debug==True: 	
			cv2.imshow('Webcam', self.frame)
		
		if cv2.waitKey(1) & 0xFF == ord('q'):   # Press Q on keyboard to stop reproducing the camera
			print("return in green webcamThread")
			self.stop()
			return
		
		#last calculation after the loop
		#print("last before rppg. red : "+str(len(red_means))+ " and times: "+str(len(times)))	
		'''		
		try:
			self.bpm=bpm_elaboration(self.means, self.fps,self.times)
			bpms.append([time.clock()-self.t0, int(self.bpm)])
		except ValueError as e:								#the butterworth doesn't work
			print(" last bpm.ValueError: {0}".format(e))
			self.vs.stop()
			cv2.destroyAllWindows()
			return -1
		except Exception as e :
			print("last calculation. Unknown error: " + ( str(e)))
			self.vs.stop()
			cv2.destroyAllWindows()
			return -2
		'''
	
	
	
	


