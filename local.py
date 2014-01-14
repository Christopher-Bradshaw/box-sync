import sys
import glob

# Given a full path, grabs the filename
def short_name(fname):
	sname = fname.split('/')[-1]
	if not sname:
		sname = fname.split('/')[-2]
	if not sname:
		sname = "ROOT"
	return(sname)

def listdir(hidden):
	if hidden:
		return(os.listdir('.'))
	else:
		return(glob.glob('*'))
	

def dash_h(data):
	for i in range(1, len(data)):
		if data[i][:2] == "-h":
			return(1)
	return(0)
		
def depth(data):
	for i in range(1, len(data)):
		if data[i][:2] == "-r":
			try:
				val = int(data[i][3])
				return(val)
			except:
				return(-1)
	return(sys.maxint)
	
		
	
		
