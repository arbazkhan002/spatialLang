#~ Extracts degenerate locative expression in a description and seperates them as [ [ [le ], [ ] ] ,[ [..] [..] .. ] , ... ]
#~ < < description <sent <le>, <le> >,  <sent <le>, <le> >, < description <sent <le>, <le> >,  <sent <le>, <le> > >
def extract_degenerate_LEs(f=open("/home/arbazk/MTT/UniMelb/Code/Dependencies exploitation/gitStore/result_felix_above20.txt")):
	les=[]
	le=""
	sent_le=[]	
	for f_l in f:
		if f_l=="\n":
			les.append(le)
			sent_le.append(les)
			le=""
			les=[]		
		else:
			#~ print f.read()
			last=f_l.split()[-1]
			pos=f_l.split()[1]
			chunk=f_l.split()[11]
			first=f_l.split()[0]
			if last == "B-NP":
				if le!="":
					les.append(le)
				le=""	
				le+=first+"_"+pos+"_"+chunk+" "
				
			elif last == "I-NP":
				le+=first+"_"+pos+"_"+chunk+" "
			else:
				if le!="":
					les.append(le)
				le=""
				
	return sent_le

def get_prep(word):
	rev_ind=word[::-1].find("_")
	ind=len(word)-rev_ind-1
	return word[ind+1:]

class Degenerate_LE:
	def __init__(self,
				prep=None,
				place_name=None):
		self.prep=prep
		self.place=place_name
	
	def get_prep(self):
		return self.prep
		
	def get_place(self):
		return self.place					

if __name__=="__main__":
	print extract_degenerate_LEs()
