import argparse
import os.path
import sys
from pathlib import Path

parentPath=str(Path(__file__).resolve().parents[1])
sys.path.append(parentPath)

import HRV.HRVWebcam as web

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser(description='Chooses what webcam this script will use.')
	
ap.add_argument("-w", "--webcam", type=int, default=0,
	help="the number of the camera available to use as webcam")

args = vars(ap.parse_args())

hearthrate=0

# use the webcam
print("webcam used : "+str(args["webcam"]))
notFinished=True
toomanyExceptions=0
while (notFinished and toomanyExceptions<6):
	try:
		hearthrate=web.rHRVElaboration(args["webcam"])
		if(hearthrate[-1][1]>0):
			notFinished=False
			print("[info "+os.path.basename(__file__)[:-3]+"] The heart rate should be:" +str(hearthrate[-1][1]))
			print(hearthrate[-1])	
		else:
			toomanyExceptions+=1
			if(hearthrate==-3):
				print("[info "+os.path.basename(__file__)[:-3]+"] Time's over and no results. Sorry")
				break
		
	except ValueError as ve:
		print("[exception "+os.path.basename(__file__)[:-3]+"] ValueError: {0}".format(ve))
		toomanyExceptions+=1
		
if(toomanyExceptions>5):
	print("[info "+os.path.basename(__file__)[:-3]+"] Too many exception found. Terminating the program...")
	


	
