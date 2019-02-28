# import the necessary packages
from threading import Thread
import cv2

class WebcamVideoStream:
	def __init__(self, src=0):
		# initialize the video camera stream and read the first frame
		# from the stream
		self.stream = cv2.VideoCapture(src)
		(self.grabbed, self.frame) = self.stream.read()
		# where i save the frames
		self.frames=list()
		# initialize the variable used to indicate if the thread should
		# be stopped
		self.stopped = False

	def start(self):
		# start the thread to read frames from the video stream
		#print("[info webcamStreamForHRV] : start")
		self.t = Thread(target=self.update, args=())
		self.t.daemon = True
		self.t.start()
		return self

	def update(self):
		# keep looping infinitely until the thread is stopped
		while True:
			# if the thread indicator variable is set, stop the thread
			if self.stopped :
				print ("stop: "+ str(self.stopped))
				return
			# otherwise, read the next frame from the stream
			(self.grabbed, self.frame) = self.stream.read()
			self.frames.append(self.frame)
			#print("hello")
		

	def read(self):
		# return the frame most recently read
		return self.frame

	def getNewFrames(self):
		#give the new batch
		return self.frames
		
	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True
		self.stream.release()
	
	def getHeight(self):
		return int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT ))
		
	def getWidth(self):
		return int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH ))