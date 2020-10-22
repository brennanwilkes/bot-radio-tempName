import sys


PREFIX_PATH = sys.path[0]
DEFAULT_TOKEN_PATH = PREFIX_PATH+"/auth/"



#Checks for a requirement file and returns the data
def getTokenFromFile(fn,path=DEFAULT_TOKEN_PATH):

	#Load token
	try:
		fname = open(path+fn, "r")
		token = fname.read().strip()
	except IOError:
		raise Exception("Please create file "+ path+fn)
	else:
		fname.close()
		return token

def commaSeparator(seq):
	return ' and '.join([', '.join(seq[:-1]), seq[-1]] if len(seq) > 2 else seq)
