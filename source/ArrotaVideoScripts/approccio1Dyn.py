import cv2
import numpy as np
import sys
from pathlib import Path
import os.path

try:
	from funzioni1 import bpm_elaboration
except ImportError:
	from .funzioni1 import bpm_elaboration

sourcePath=str(Path(__file__).resolve().parents[1])
	
def dynGreenElaboration(filepath, showVideo=False):
	'''
	Script adapted from the arrota project from the webcam to the video use
	It uses the ica mode to calculate the bpm series
	'''

	#variables
	bpms= list()					# a series with the second in question and the bpm calculated for that second
	means = list()
	firstTime = True
	secondOfFrame=10				# the window of seconds on which clear the means saved. 10 seconds for default
									# 1 means that every second after the calculation it will clear the means lists
	secondsBeforeNewLine=20			# cosmetic variable to set after how many second-points it should have a new line
	fps=0							# in a video, the fps is known
	videoLen=0						# the number of frames in the video
	
	
	cap = cv2.VideoCapture(filepath)
	
	if (cap.isOpened() == False): 
		print("Unable to read the video")
		
	# Find OpenCV version
	(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
	
	#Taking the fps of the video and the number of frames of it
	if int(major_ver)  < 3 :
		fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)	
		videoLen=int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
	else :
		fps = cap.get(cv2.CAP_PROP_FPS)
		videoLen=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	
	face_cascade = cv2.CascadeClassifier(os.path.join(sourcePath,'haarcascade_frontalface_default.xml'))
	print("[info dynGreenElaboration] Processing the video with the dynamic green mode...")
		
	#print("[info dynGreenElaboration]the fps of the video is: "+str(fps)+" , "+ "and the number of frames is: "+str(videoLen) )
	#print("[info dynGreenElaboration]please wait while it is calculating:")
	for currentFrame in range(0, videoLen):
		ret, frame = cap.read()
		#print(frame)
		try:
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			#Face detection
			faces = face_cascade.detectMultiScale(gray, 1.3, 5)

			if len(faces) == 1:
				for (x,y,w,h) in faces:
					reducedWidth = int(w * 0.63)
					modifiedX = int(w * 0.15)
					reduceHeigh = int(h * 0.25)
					inizioY = int(h * 0.1)
					fronteX = int(w - reducedWidth)
					fronteY = int(h - reduceHeigh)
					
					face = frame[y:y+h, x+modifiedX:x+w-modifiedX]
					if firstTime:
						foreheadX = x+fronteX
						foreheadY = y+inizioY
						foreheadX2 = x+reducedWidth
						foreheadY2 = y+reduceHeigh
						firstTime = False	
					fronte = frame[foreheadY: foreheadY2, foreheadX:foreheadX2]						
					#forehead detection
					green = fronte[:,:,1]
					fronte = np.zeros((green.shape[0], green.shape[1], 3), dtype = green.dtype)
					fronte[:,:,1] = green
					means.append(np.mean(fronte[:,:,1]))
					
			else: 					# se non c'è una faccia come media mette la media precedente
				if len(means) > 0:
					means.append(means[len(means)-1])
			#calculates not for each frame but for each second more or less		
			if(currentFrame>0 and currentFrame%fps==0):
				if(int(currentFrame/fps)%secondOfFrame==0):
					bpm = bpm_elaboration(means, fps)
					bpms.append([currentFrame/fps,bpm])
					means=[]
					
				print ('.' , end='', flush=True) 					# 1 point displayed for second
				if(int(currentFrame/fps)%secondsBeforeNewLine==0):
					print()
			# show the skin in video
			if(showVideo):
				cv2.rectangle(frame, (foreheadX, foreheadY), (foreheadX2, foreheadY2), (0,255,0), 2) # the rectangle that will show on the forehead
				
			if(showVideo):	#show the video
				cv2.imshow('Video', frame)
				if cv2.waitKey(1) & 0xFF == ord('q'):
					break				
		except Exception as e:
			print("[exception dynGreenElaboration] At frame: "+ str(currentFrame)+" of "+str(videoLen) +" there is no frame. Terminating...")
			#print("[exception dynGreenElaboration] cap.opened: "+str(cap.isOpened()))
			break	#just for now
			
	#bpm = bpm_elaboration(means, fps)
	print()								# putting the next print after a new line having a clean text
	
	# clear up the capture
	cap.release()
	return bpms


