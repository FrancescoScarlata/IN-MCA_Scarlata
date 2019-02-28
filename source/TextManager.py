


class TextManager :
	'''
	
	This is a class that manages to write on a path given at the creation of the instance.
	
	'''
	def __init__(self, filePath):
		self.filePath=filePath
		print("init textManager")

	def write(self, text):
		'''
			Writes the string given in input on the file.
			It opens and closes everytime the file i/o 
		'''
		print("[info TextManager] write  text: "+text)
		try:
			file = open(self.filePath, "a+") 
			file.write(text+"\n")
			file.close() 
		except Exception:
			print("Exception when writing")