import cv2
import numpy as np
import time
from cameraUtils import WebcamStreamForHRV as web
from pathlib import Path
import os.path

try:
	import functions
except ImportError:
	from HRV import functions

sourcePath=str(Path(__file__).resolve().parents[1])
	
def determineMeans(vs,red,green,blue,oldTimes, x1, y1, x2, y2):
	'''
	This function is called for make the mean frames.
	It will:
	- call the webcam stream to get the frames and times
	- determine the means 
	- return the lists
	'''
	frames, times = vs.getFramesAndTime() # reads from the vs
	#It will add the mean of just the new ones
	if(len(red) < len(frames)):
		for i in range(len(red),len(frames)): # frames in rgb. the frame is BGR
			red.append(np.mean(frames[i][y1:y2,x1:x2,2]))
			green.append(np.mean(frames[i][y1:y2,x1:x2,1]))
			blue.append(np.mean(frames[i][y1:y2,x1:x2,0]))
			oldTimes.append(times[i])

	return red,green, blue, oldTimes

def rHRVElaboration(camSource):
	""" 
	This script is responsible for the main behaviour of the feature.
	 It should:
	 1) activate and release the camera in order to capture the frames
	 2) read the frames- > from a thread
	 3) do the face detection & relative skin detection
	 4) Uniform samples (in time)
	 5) Average of the skin pixel to obtain a triplet of RGB values
	 6) Concatenate the triplets to obtain the RGB temporal trace.
	 7) Traces pre-processed by zero-mean
	 8) Detrend using smoothness priors approach
	 9) band-pass filtered with Butterworth filter (cut off freqs 0.7 and 3.5Hz)
	 10) Extraction of the rPPG signal using CHROM (chrominance-based method)
	 11) Calculate peaks in the rPPG signal to calcolate the rHRV signal.
	 12) calculate the mean ibi to determine the heart rate
	 NOTE: some of the script is taken from the Arrotta IN project, 
		   this is an acknowledgement to that.
	 """
	# calling the thread responsible for the webcam readings 
	vs = web.WebcamStreamForHRV(src=camSource).start() #to change when this becomes a function


	frame_width = vs.getWidth()
	frame_height = vs.getHeight()
	#print( str(frame_height) + "    " + str(frame_width))
	face_cascade = cv2.CascadeClassifier(os.path.join(sourcePath,'haarcascade_frontalface_default.xml')) # taks the cascade classifier

	# Variables
	redCol = (0, 0, 255) 		# red color in BGR
	greenCol= (0, 255, 0)
	tsize = 3					#Dimension of the time elements

	max_samples = 300			# number of frames to collect before end
	remaining = -1      		# const to say when it is the end
	times = list()
	red_means = list()		# the list of the forehead component means
	green_means = list()
	blue_means = list()
	t0=0
	bpm=0
	bpms=list()

	firstTime= True
	timeBetweenCalculations=0 	#a variable to wait before recalculate the hrv

	# variables to not calculate everytime
	leftOffset=				int(frame_width/21) 		# around 30 in offeset with 640 as frame width
	highHeightOffset=		int(frame_height* 3/24) 	# 60 in offeset with 480 as frame height
	lowHeightOffset=		int(frame_height* 21/24) 	# 420 in offeset with 480 as frame height
	heightOffsetSeconds=	int(frame_height* 5/24) 	# 100 in offeset with 480 as frame height

	fps=1 # just a default value to define the variable
	# first loop: it takes the frames, saves the means and works on them
	while(True):
		frame = vs.read()
		if time.clock() > 3:    		# skip the first seconds to setup the focus of the camera
			if 0 <= max_samples-len(red_means) and remaining!=-1:
				cv2.putText(frame, str(remaining), (leftOffset, heightOffsetSeconds), 
				cv2.FONT_HERSHEY_SIMPLEX, tsize, redCol) 		# the countdown displayed

			#Face detection
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			faces = face_cascade.detectMultiScale(gray, 1.3, 5)

			if len(faces) == 1: 		#if the detection is of just 1 face 
				cv2.putText(frame, "Please, don't move", (leftOffset, lowHeightOffset), cv2.FONT_HERSHEY_SIMPLEX, tsize-2, redCol, 1, cv2.LINE_AA)  # just a warning
				for (x,y,w,h) in faces:
					 # static Skin detection
					reducedWidth = int(w * 0.63)
					modifiedX = int(w * 0.15)
					reduceHeigh = int(h * 0.25)
					inizioY = int(h * 0.1)
					frontX = int(w - reducedWidth)

					
					# Picking the coordinates of the forehead
					foreheadY = y+inizioY	
					foreheadX = x+frontX
					foreheadX2 = x+reducedWidth
					foreheadY2 = y+reduceHeigh
						
					if firstTime:
						firstTime = False
						t0 = time.clock()			# initial time
						vs.startSaving()	
					cv2.rectangle(frame, (foreheadX, foreheadY), (foreheadX2, foreheadY2), greenCol, 2) # the rectangle that will show on the forehead
			else:
				if len(faces) == 0:
					cv2.putText(frame, "No face detected...", (leftOffset, lowHeightOffset), cv2.FONT_HERSHEY_SIMPLEX, 1, redCol)
				else:
					cv2.putText(frame, "Too many faces...", (leftOffset, lowHeightOffset), cv2.FONT_HERSHEY_SIMPLEX, 1, redCol)

			if len(times) > 9 and len(red_means)>0:      # wait some frames before to start the calculations of the bpm
				#the calculation
				# calculates not for each frame but for each second more or less, because the user won't understand the difference between time+0.5 or time +1 seconds 
				if time.clock()-timeBetweenCalculations>= 1 :			
					timeBetweenCalculations=time.clock()
					 
					# determines the means for the new frames
					if(not vs.isNotSaving):
						red_means,green_means,blue_means,times = determineMeans(vs,red_means,green_means,blue_means, times, foreheadX, foreheadY, foreheadX2, foreheadY2 )
					#print("After determine red : "+str(len(red_means))+ "and times: "+str(len(times)))
					
					if not len(times) == len(red_means): 					# when the two lenghts are different, for some reasons
						print("[info check len(times) != len(red_means)] different len: "+str(len(times))+" , "+ str(len(red_means)))
						red_means = functions.adjustList(red_means, times)
						green_means = functions.adjustList(green_means, times)
						blue_means = functions.adjustList(blue_means, times)
					
					fps = functions.fps_elaboration(times)

					bpm,state=functions.hrElaboration(red_means, green_means, blue_means, times, fps)
					bpms.append([time.clock()-t0, int(bpm)])
					if(fps*30>250):
						max_samples=int(fps)*30
				else:
					remaining = int(35+t0-time.clock()) 	#probably to change with a dynamic remaining
					
					#print("time passed after the last check: "+ str(timeBetweenCalculations))
				if(bpm>0)	:
					cv2.putText(frame, "bpm: " + str(int(bpm)), (foreheadX-25, foreheadY-45), cv2.FONT_HERSHEY_SIMPLEX, tsize-2, redCol) # display the bpm	
			else:
				cv2.putText(frame, "Starting...", (leftOffset, highHeightOffset), cv2.FONT_HERSHEY_SIMPLEX, 1, redCol)	# second message
				cv2.putText(frame, "Please, don't move", (leftOffset, lowHeightOffset+40), cv2.FONT_HERSHEY_SIMPLEX, tsize-2, redCol, 1, cv2.LINE_AA) # just a warning
				if time.clock()-timeBetweenCalculations>= 1 :			# i'm trying to calculate not for each frame but for each second more or less, to increase the fps
					timeBetweenCalculations=time.clock()
					# determines the means for the new frames
					if(not vs.isNotSaving):
						red_means,green_means,blue_means,times= determineMeans(vs,red_means,green_means,blue_means, times, foreheadX, foreheadY, foreheadX2, foreheadY2)
					cv2.imshow('Webcam', frame)
				
		else:
			cv2.putText(frame, "Loading...", (leftOffset, highHeightOffset), cv2.FONT_HERSHEY_SIMPLEX, tsize-2, redCol) # first message
			cv2.putText(frame, "Please, take off your glasses", (leftOffset, lowHeightOffset), cv2.FONT_HERSHEY_SIMPLEX, tsize-2, redCol, 1, cv2.LINE_AA) # just a warning
			cv2.imshow('Webcam', frame)

		if time.clock() >= 180:
			print("[Debug time clock>180] over the time break")
			vs.stop()
			cv2.destroyAllWindows()
			return -3
		
		if len(times) >= max_samples:
			#print("times> max samples. red : "+str(len(red_means))+ "and times: "+str(len(times)))
			break

		cv2.imshow('Webcam', frame)
		
		if cv2.waitKey(1) & 0xFF == ord('q'):   # Press Q on keyboard to stop reproducing the camera
		  break
	
	#last calculation after the loop
	#print("last before rppg. red : "+str(len(red_means))+ " and times: "+str(len(times)))		
	try:
		bpm,state=functions.hrElaboration(red_means, green_means, blue_means, times, fps,True)
		bpms.append([time.clock()-t0, int(bpm)])
	except ValueError as e:								#the butterworth doesn't work
		#print(" last bpm.ValueError: {0}".format(e))
		vs.stop()
		cv2.destroyAllWindows()
		return -1
	except Exception as e :
		print("last calculation. Unknown error: " + ( str(e)))
		vs.stop()
		cv2.destroyAllWindows()
		return -2
		
	#print("[info] the calculated bpm is : " + str(bpm))
	vs.stopSaving()
	
	# second loop:  show the result but it doesn't compute anymore
	while(True): 		
		frame = vs.read()
		cv2.putText(frame, "Press 'q' to quit", (leftOffset, highHeightOffset), cv2.FONT_HERSHEY_SIMPLEX, 1, redCol)
		cv2.putText(frame, "Final bpm: " + str(int(bpm)), (leftOffset, heightOffsetSeconds), cv2.FONT_HERSHEY_SIMPLEX, 1, redCol)
		cv2.imshow('Webcam', frame)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	# do a bit of cleanup
	vs.stop()
	cv2.destroyAllWindows() 
	return bpms