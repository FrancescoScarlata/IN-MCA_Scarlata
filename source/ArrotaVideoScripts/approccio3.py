import cv2
import numpy as np
import _thread
from pathlib import Path
import os.path

try:
	from funzioni3 import  pca_bpms, PCAAlg
except ImportError:
	from .funzioni3 import pca_bpms, PCAAlg

sourcePath=str(Path(__file__).resolve().parents[1])
	
def pcaElaboration(filepath, showVideo=False):

	'''
		This script is adapted from the "approccio 3" of the arrota project for videos
		It uses the pca mode to calculate the bpm series
	'''
	
	#variables
	bpms = list()
	face_red_means = list()			# means series for the face
	face_green_means = list()
	face_blue_means = list()
	fps=0							# in a video, the fps is known
	videoLen=0						# the number of frames in the video
	secondsBeforeNewLine=20			# cosmetic variable to set after how many second-points it should have a new line
	
	cap = cv2.VideoCapture(filepath)

	# Find OpenCV version
	(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
	
	#Taking the fps of the video and the number of frames of it
	if int(major_ver)  < 3 :
		fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)	
		videoLen=int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
	else :
		fps = cap.get(cv2.CAP_PROP_FPS)
		videoLen=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	
	if (cap.isOpened() == False): 
		print("Unable to read camera feed")
	 
	face_cascade = cv2.CascadeClassifier(os.path.join(sourcePath,'haarcascade_frontalface_default.xml'))
	print("[info pcaElaboration] processing the video with the pca mode...")

	for currentFrame in range(0, videoLen):
		ret, frame = cap.read()
		try: 
			#face detection
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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
					face_red_means.append(np.mean(face[:,:,0]))
					face_green_means.append(np.mean(face[:,:,1]))
					face_blue_means.append(np.mean(face[:,:,2]))
			else:
				if len(face_red_means) > 0 and len(face_green_means) > 0 and len(face_blue_means) > 0:
					face_red_means.append(face_red_means[len(face_red_means)-1])
					face_green_means.append(face_green_means[len(face_green_means)-1])
					face_blue_means.append(face_blue_means[len(face_blue_means)-1])
			
			# show the skin in video
			if(showVideo):
				cv2.rectangle(frame, (x+modifiedX, y), (x+w-modifiedX, y+h), (0,255,0), 2) # the rectangle that will show on the forehead
			
			#calculates not for each frame but for each second more or less		
			if(currentFrame>0 and currentFrame%fps==0):
				bufFace = list()
				bufFace.append(face_red_means)
				bufFace.append(face_green_means)
				bufFace.append(face_blue_means)
				dati_faccia = np.ndarray(shape = (3, len(face_red_means)), buffer = np.array(bufFace))
				# times is not used in that function. parameter can be deleted after asked to the teacher
				_thread.start_new_thread(PCAAlg, (dati_faccia, fps)) 

				if(len(pca_bpms)>0):
					bpm = pca_bpms[-1]
					bpms.append([currentFrame/fps,bpm])
				print ('.' , end='', flush=True) 					# 1 point displayed for second
				if(int(currentFrame/fps)%secondsBeforeNewLine==0):
					print()
					
			if(showVideo):	#show the video
				cv2.imshow('Video', frame)

				if cv2.waitKey(1) & 0xFF == ord('q'):
					break
						
		except Exception as e:
			print("[exception pcaElaboration] At frame: "+ str(currentFrame)+" of "+str(videoLen) +" there is no frame. Terminating...")
			#print("[exception pcaElaboration] cap.opened: "+str(cap.isOpened()))
			break	#just for now
	print()
	cap.release()
	return bpms



