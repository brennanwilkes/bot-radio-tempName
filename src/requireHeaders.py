import sys

PREFIX_PATH = sys.path[0]
DEFAULT_TOKEN_PATH = PREFIX_PATH+"/auth/"



#Checks for a requirement file and returns the data
def requireFile(fn,path=DEFAULT_TOKEN_PATH):

	#Load token
	try:
		fname = open(path+fn, "r")
		token = fname.read().strip()
	except IOError:
		raise Exception("Please create file "+ path+fn)
	else:
		fname.close()
		return token
