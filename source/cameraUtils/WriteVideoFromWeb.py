import numpy as np
import cv2
import argparse

'''
This script saves a video file named 'x.avi' where x is the name given in input or "output"
This is just a try to see the given fps
'''

cap = cv2.VideoCapture(0)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser(description='Save the video from webcam and choose the name.')
ap.add_argument("-n", "--name", default='output', help="The name of the video to save. Default: output")

args = vars(ap.parse_args())


namefile=args["name"]+'.avi'
# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
#out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
out = cv2.VideoWriter(namefile, fourcc, 20.0, (640,480))

while(cap.isOpened()):
	ret, frame = cap.read()
	if ret==True:

		# write the frame
		out.write(frame)

		cv2.imshow('frame',frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	else:
		break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()