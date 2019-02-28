# import the necessary packages
from __future__ import print_function
import WebcamStreamForHRV
from imutils.video import FPS
import argparse
import imutils
import cv2
import sys
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--numFrames", type=int, default=100,
	help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
	help="Whether or not frames should be displayed")
args = vars(ap.parse_args())

# grab a pointer to the video stream and initialize the FPS counter
print("[INFO] sampling frames from webcam...")
stream = cv2.VideoCapture(0)
fps = FPS().start()
 
# loop over some frames
while fps._numFrames < args["numFrames"]:
	print(str(args["numFrames"]))
	# grab the frame from the stream and resize it to have a maximum
	# width of 400 pixels
	(grabbed, frame) = stream.read()
 
	# check to see if the frame should be displayed to our screen
	if args["display"] > 0:
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF
 
	# update the FPS counter
	fps.update()
 
# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
 
# do a bit of cleanup
stream.release()
cv2.destroyAllWindows()

# created a *threaded* video stream, allow the camera sensor to warmup,
# and start the FPS counter
print("[INFO] sampling THREADED frames from webcam...")
vs = WebcamStreamForHRV.WebcamStreamForHRV(src=0).start()
fps = FPS().start()
 
x=0
done=False
# loop over some frames...this time using the threaded stream
while fps._numFrames < args["numFrames"]:

	frame = vs.read()

	if(x<20):
		x=x+1
	else:
		if(not done):
			done=True
			vs.setPositions(50,200,100,400)
			
	cv2.rectangle(frame, (50, 200), (100, 400), (0,0,255) , 2) # the rectangle that will show on the forehead
 
	# check to see if the frame should be displayed to our screen
	if args["display"] > 0:
		cv2.imshow("Frame", frame)
		if(len(vs.getNewFrames())>1):
			#print(len(vs.getNewFrames()))
			cv2.imshow("little", vs.getLittleImg())
		key = cv2.waitKey(1) & 0xFF
	
	
	# update the FPS counter
	fps.update()
 
# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
 
# do a bit of cleanup
vs.stop()

cv2.destroyAllWindows()




