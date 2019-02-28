# import the necessary packages
from threading import Thread
import cv2
import time

try:
	from WebcamVideoStream import WebcamVideoStream
except ImportError:
	from .WebcamVideoStream import WebcamVideoStream
	
class WebcamStreamForHRV(WebcamVideoStream):

	def __init__(self,src=0):
		'''
			initialize the stream in the father init
		'''
		#print("[info webcamStreamForHRV] : init")
		self.isNotSaving=True 	# a bool to break when the skin is detected
		self.times=list()
		super().__init__(src)
	
	
	
	def update ( self ):
		#print("[info webcamStreamForHRV] : update")
		# keep looping infinitely until the it's ready to save
		while self.isNotSaving: 
			(self.grabbed, self.frame) = self.stream.read() # just read the frames
		
		#print("let's start to save")
		self.t0=time.time()
		# keep looping infinitely until the thread is stopped
		while not self.isNotSaving:
			# if the thread indicator variable is set, stop the thread
			if self.stopped :
				#print ("stop: "+ str(self.stopped))
				return
			# otherwise, read the next frame from the stream
			(self.grabbed, self.frame) = self.stream.read()
			self.frames.append(self.frame)
			self.times.append(time.time()-self.t0)
			#print("hello")
		
		while self.isNotSaving: 
			(self.grabbed, self.frame) = self.stream.read() # just read the frames
			if self.stopped :
				#print ("stop: "+ str(self.stopped))
				return
			
	def startSaving(self):
		'''
			Starts ti save the images
		'''
		self.isNotSaving=False
		return "saving now"
	
	def getLittleImg(self):
		return self.frames[-1]
		
	def getFramesAndTime(self):
		frames=self.frames
		times=self.times
		
		self.frames=list()
		self.times=list()
		
		return frames, times
	
	def isNotSaving(self):
		return self.isNotSaving
		
	def stopSaving(self):
		self.isNotSaving=True