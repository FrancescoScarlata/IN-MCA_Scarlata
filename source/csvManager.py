import csv

def readLines(filename, names):
	''' this method will give the lines in output (with just the columns given in names) '''
	lines=list()
	with open(filename, newline='') as csvfile:
		try:
			reader = csv.DictReader(csvfile)
			for row in reader:
				line=[]
				for name in names:
					line.append(row[name])
				lines.append(line)		
		except Exception:
			return readHrLines(filename)
	return lines
	
def readHrLines(filename):
	''' This method is made specifically for when there is a csv with just secs and bpm without headers '''
	lines=list()
	with open(filename, newline='') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			lines.append([row[0],row[1]])
			#print(row)
	return lines		

def checkVideofileIsSaved(resultsName,videofile):
	''' check if the file has a row with the videofilename asked '''
	with open(resultsName, newline='') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if(row['videofile_name']==videofile):
				return True
	return False

def writeMeanValues(resultName,videofile,names,means,resultsExists):
	'''
		Writes the result
	'''
	with open(resultName, 'a', newline='') as csvfile:
		fieldnames = ['videofile_name', 'hr_nameMethod', 'mean_distance' ]
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		if( not resultsExists):
			writer.writeheader()
		for i in range(0, len(means)):
			writer.writerow({'videofile_name': videofile, 'hr_nameMethod': names[i],'mean_distance': means[i]})

def readMeanValues(resultName):
	'''
	This will read the mean distance from the csv result file.
	The shape to give will be nxm where:
	n is the number of video file saved
	m is the number of methods used (in this case 3) with the mean distance
	'''
	lines=list()
	with open(resultName, newline='') as csvfile:
		reader = csv.DictReader(csvfile)
		reader=list(reader)
		index=0

		while(index<len(reader)-1):
			videofile=reader[index]['videofile_name']
			line=[]
			for i in range (index, len(reader)):
				if(videofile==reader[i]['videofile_name']and i<len(reader)-1):
					line.append([reader[i]['hr_nameMethod'],reader[i]['mean_distance']])	# records per video file with the name of the method and the mean distance
				else:
					if(i==len(reader)-1):
						line.append([reader[i]['hr_nameMethod'],reader[i]['mean_distance']])
					index=i
					break
					print ('.' , end='', flush=True)
			lines.append(line)			
	return lines
	
	
			
if __name__=="__main__":
	csvFile=readLines('physio_1.csv', ['timestamp','hr'])
	#for i in range(0, len(csvFile)):
	#	print( csvFile[i])
	print("\n Second round \n")
	csvFile2=readHrLines('data.csv')
	for i in range(0, len(csvFile2)):
		print("line "+str(i)+": "+ str(csvFile2[i]))