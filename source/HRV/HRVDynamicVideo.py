import cv2
import numpy as np
from pathlib import Path
import os.path
import sys
try:
	import functions
except ImportError:
	from HRV import functions

sourcePath=str(Path(__file__).resolve().parents[1])

def dynHrvElaboration(videofilepath,showImages=False, showVideo=False, showArousal=False):
	''' 
		This script calculate the hr every second and pass them to the caller.
		It :
		1) opens the video
		2) reads the frames
		3) does the face detection & relative skin detection
		4) Average of the skin pixel to obtain a triplet of RGB values
		5) Concatenate the triplets to obtain the RGB temporal trace.
		6) Does the process (in the functions method) with CHROM
		7) calculate the hr 
	'''

	## Variables
	face_red_means = list()			# the lists of the forehead means
	face_green_means = list()
	face_blue_means = list()
	bpms= list()					# a series with the second in question and the bpm calculated for that second				
	firstTime= True
	secondOfFrame=10				# the window of seconds on which clear the means saved. 
									# 1 means that every second after the calculation it will clear the means lists
	secondsBeforeNewLine=20			# cosmetic variable to set after how many second-points it should have a new line
	fps=0							# in a video, the fps is known
	videoLen=0						# the number of frames in the video	
	startFrame=0					# the frame that starts the window
	emotionalFeatures=list()
	
	
	cap = cv2.VideoCapture(videofilepath)  # open the video
	if (cap.isOpened() == False): 
		print("[info dynHrvElaboration] Unable to read the video")

	print("[info dynHrvElaboration] Processing the video with the dynamic hrv mode...")
	 # Find OpenCV version
	(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
	
	#Taking the fps of the video and the number of frames of it
	if int(major_ver)  < 3 :
		fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)	
		videoLen=int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))	
	else :
		fps = cap.get(cv2.CAP_PROP_FPS)
		videoLen=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
		
	# for now we assume that the script calling is in a subfolder too
	face_cascade = cv2.CascadeClassifier(os.path.join(sourcePath,'haarcascade_frontalface_default.xml'))

	print("[info dynHrvElaboration] The fps of the video is: "+str(fps)+" , "+ "and the number of frames is: "+str(videoLen) )
	print("[info dynHrvElaboration] Please wait while it is calculating:")
	# first loop: it takes the frames, saves the means and works on them. no display of the video, just a . every second
	for currentFrame in range(0, videoLen):
		ret, frame = cap.read()
		if(frame is not None):
			#try:
				
			#Face detection
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			faces = face_cascade.detectMultiScale(gray, 1.3, 5)

			if len(faces) == 1: 		#if the detection is of just 1 face 
				for (x,y,w,h) in faces:
					 # static Skin detection
					reducedWidth = int(w * 0.63)
					modifiedX = int(w * 0.15)
					reduceHeigh = int(h * 0.25)
					inizioY = int(h * 0.1)
					frontX = int(w - reducedWidth)
					
					if firstTime:
					# locking the coordinates of the forehead
						foreheadY = y+inizioY	
						foreheadX = x+frontX
						foreheadX2 = x+reducedWidth
						foreheadY2 = y+reduceHeigh
						#firstTime = False
					
					rawForehead = frame[foreheadY:foreheadY2, foreheadX:foreheadX2]
					face_red_means.append(np.mean(rawForehead[:,:,2]))
					face_green_means.append(np.mean(rawForehead[:,:,1]))
					face_blue_means.append(np.mean(rawForehead[:,:,0]))
			else:
				if len(faces) == 0:
					print("[info dynHrvElaboration] no face detected in a frame")
				else:
					print("[info dynHrvElaboration] too many faces detected in a frame")
					
				if not firstTime : 	#maybe an error of the cascade, but the video should be done with the subject not moving					
					rawForehead = frame[foreheadY:foreheadY2, foreheadX:foreheadX2]
					face_red_means.append(np.mean(rawForehead[:,:,2]))
					face_green_means.append(np.mean(rawForehead[:,:,1]))
					face_blue_means.append(np.mean(rawForehead[:,:,0]))
			
			# show the skin in video
			if(showVideo):
				cv2.rectangle(frame, (foreheadX, foreheadY), (foreheadX2, foreheadY2), (0,255,0), 2) # the rectangle that will show on the forehead
					
			#calculates not for each frame but for each second more or less		
			if (currentFrame>0 and currentFrame%fps==0) :	
				print ('.' , end='', flush=True) 					# 1 point displayed for second
				if(int(currentFrame/fps)%secondsBeforeNewLine==0):
					print()
				if(int(currentFrame/fps)%secondOfFrame==0):
					try:				# determine the hr just onece for frame
						#print("len of face "+str(len(face_red_means)))
						bpm,sf = functions.hrElaboration(face_red_means, face_green_means, face_blue_means, None, fps, showImages ,False, True, currentFrame, startFrame,showArousal)
						#print( "bpm: "+str(bpm))
						bpms.append([currentFrame/fps,bpm])
						emotionalFeatures.append([currentFrame/fps,sf])
					except Exception as e :
						print()
						print("[exception dynHrvElaboration] exception! Unknown error: " + ( str(e))+ " in line:"+ str( sys.exc_info()[-1].tb_lineno))
						bpms.append([currentFrame/fps,np.nan])	#instead of not going on, just pass a nan that will be ignored in the 
					face_red_means=[]
					face_green_means=[]
					face_blue_means=[]
					startFrame=currentFrame
					
			if(showVideo):	#show the video
					cv2.imshow('Video', frame)

					if cv2.waitKey(1) & 0xFF == ord('q'):
						break
		else:
			print("[exception dynHrvElaboration] Null frame at frame: "+ str(currentFrame)+" of "+str(videoLen) +".")
			break # just for now
	print()		

	if( showArousal): #shows the arousal feature normalized on the first element
		hr=list()
		arousal=list()
		times=list()
		for i in range(0,len(bpms)):
			hr.append(bpms[i][1])
			times.append(bpms[i][0])
			arousal.append(emotionalFeatures[i][1])
		arousal/=arousal[0]
		
		functions.plotHRAndArousal(times,times,hr,arousal)

	cap.release()	
	return bpms, emotionalFeatures
	
	