import sys
import glob

# Given a full path, grabs the filename
# If path is ROOT ("/"), returns "ROOT"
def short_name(fname):
	sname = fname.split('/')[-1]
	if not sname:
		sname = fname.split('/')[-2]
	if not sname:
		sname = "ROOT"
	return(sname)

# returns a list of items in the directory.
# includes hidden files if hidden=True, else doesn't
def listdir(hidden):
	if hidden:
		return(os.listdir('.'))
	else:
		return(glob.glob('*'))
	
# Checks if -h is specified in this line of the settings
# Returns 1 if it is
def dash_h(data):
	for i in range(1, len(data)):
		if data[i] == "-h":
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

# Given the data read from settings, removes duplicates
# Remove the option with less depth if possible
# Algo scales badly (n^2) but n will be tiny...
def remove_duplicates(data):
	i = j = 0
	while i < len(data):
		while j < len(data):
			if i == j:
				pass
			elif data[i][0] == data[j][0]:
				if depth(data[i]) < depth(data[j]):
					data.remove(data[i])
				else:
					data.remove(data[j])
			j += 1
		i += 1
	return(data)
				
				
		

		
	
		
