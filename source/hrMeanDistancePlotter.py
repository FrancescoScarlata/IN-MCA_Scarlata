# mean distance plotter
import argparse
import csvManager as manager
import os.path
import matplotlib.pyplot as plt
from decimal import Decimal

def findPercentage(x,y,z):
	'''
		This will find the percentage for being the best for each series.
		It is given that they'll have the same length
	'''
	count=[0,0,0]
	for i in range (0, len(x)):
		if(Decimal(x[i])<Decimal(y[i]) and x[i]<z[i]):
			count[0]+=1
		else:
			if(y[i]<z[i]):
				count[1]+=1
			else:
				count[2]+=1
	
	print("\nthe number of videos in this file are : "+str(len(x)))
	print()
	print("the percentage of green hr being the best is : {0:.2f} % of the total \n".format(count[0]/len(x)*100))
	print("the percentage of pca hr being the best is : {0:.2f} % of the total \n".format(count[1]/len(x)*100))
	print("the percentage of hrv hr being the best is : {0:.2f} % of the total \n".format(count[2]/len(x)*100))
	print()

if __name__ =="__main__":
	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser(description='Write the name of the file with the mean distance to plot')

	ap.add_argument("-f", "--file", help="The name csv file.", required=True)
		
	args = vars(ap.parse_args())

	if(os.path.exists(args["file"])): # file exists
		allMeans=manager.readMeanValues(args["file"]) # shape n*3 with n the video saved
		
		# dependent but right now i don't know how to generalize it
		
		green=list()
		pca=list()
		hrv=list()
		times=list()
		for i in range(0, len(allMeans)):
			#print(allMeans[i])
			green.append(round(Decimal(allMeans[i][0][1]),2))
			pca.append(round(Decimal(allMeans[i][1][1]),2))
			hrv.append(round(Decimal(allMeans[i][2][1]),2))
			times.append(i)
		
		
		plt.figure(1)
		plt.clf()
		plt.title('Mean distance for all the video saved')
		
		plt.plot(times,green, label=allMeans[0][0][0],marker="o", ls="")
		plt.plot(times,pca, label=allMeans[0][1][0],marker="o", ls="")
		plt.plot(times,hrv, label=allMeans[0][2][0],marker="o", ls="")
		plt.axhline(y=3, color='green')
		plt.axhline(y=6, color='yellow')
		plt.axhline(y=7, color='red')
		plt.xlabel('num video in sequence')
		plt.ylabel('distance')		
		plt.ylim(ymin=0)
		plt.legend(loc='best')
		plt.show()
		
		findPercentage(green,pca,hrv)

	else:
		print("the file "+filename+" is not in source") # print will be changed after if i move the result file 


	
	
	
	
	
	
	
	
