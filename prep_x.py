DEP_POS = 2
GOV_POS = 1
REL_POS = 0
modifiers = [
			"amod" , #  adjectival modifier
			"appos" , #  appositional modifier
			"advcl" , #  adverbial clause modifier
			"det" , #  determiner
			"predet" , #  predeterminer
			"preconj" , #  preconjunct
			"infmod" , #  infinitival modifier
			"mwe" , #  multi, # word expression modifier
			"mark" , #  marker (word introducing an advcl or ccomp
			"partmod" , #  participial modifier
			"advmod" , #  adverbial modifier
			"neg" , #  negation modifier
			"rcmod" , #  relative clause modifier
			"quantmod" , #  quantifier modifier
			"nn" , #  noun compound modifier
			"npadvmod" , #  noun phrase adverbial modifier
			"tmod" , #  temporal modifier
			"num" , #  numeric modifier
			"number" , #  element of compound number
			"prep" , #  prepositional modifier
			"poss" , #  possession modifier
			"possessive" , # possessive modifier ('s)
			"prt" , #  phrasal verb particle
			]



#~ def add_to_pos(key,value):
	#~ pos_dict[key]=value

def is_None(obj):
	if obj is None:
		return 0
	else:
		return 1	

#~ Curried form of getting ith index of a list
def listGet(i):
	def get(l):
		return l[i]
	return get	

#~ index of the first element that satisfies f 
def find_fun(f,xs):
	for index,x in enumerate(xs):
		if f(x)==1:
			return index		

#~ return the set of all triplets that satisfy the provided query of rel,gov,dep
#~ Query search is for those arguments that are set to None
#~ If all are provided, there exists a unique triplet
#~ If atleast one of them is set as None, there can be more than one triplets returned
def query_triplet(t,rel=None,gov=None,dep=None):
	triplet=[rel,gov,dep]
	out=[]
	
	knowns=filter(is_None,triplet)
	#~ print  t,"####", triplet
	if len(knowns)==0:
		return t
	
	else:
		for tindex, triple in enumerate(t):
			
			#~ Check whether the intersection size is equal to the number of knowns
			if len(set(triple) & set(triplet))==len(knowns):
				
				#~ check whether the order is correct for the intersection
				index_set=map(is_None,triplet)
				
				
				temp=[]
				
				for index,value in enumerate(index_set):
					if value==1:
						temp.append(triple[index])

				if temp==knowns:	
					out.append([triple,tindex])
		return out		
		
		
def output_parser(f):
	sentences=[]
	sentence=""
	for line in f:
		if line=="\n":
			sentences.append(sentence)
			sentence=""
		else:
			sentence+=line

	for sent in sentences:
		#~ print sent
		[pos,dep] = sent.split("***")

		pos=pos.split("\n")[:-1]
		# example format of pos - ['I/PRP', 'am/VBP', 'at/IN', .. ]

		deps=dep.strip().split("\n")
		# example format of deps - ['det(house-2, The-1)', 'nsubjpass(located-4, house-2)', .... ]

		loc_dict={}					# dictionary storing words' positions
		pos_dict={}					# dictionary storing words' pos tags

		counter=0
		for tag in pos:
			key,value=tag.split("/")
			#~ print key,value
			#~ add_to_pos(key,value)
			pos_dict[key]=value
			loc_dict[key]=counter
			counter+=1
		
		triples = []					
		raw_triples = []			#triples with the word postions
		for rel in deps:
			s=rel
			raw_gov,raw_dep=s[s.find("(")+1:s.find(")")].split(",")
			raw_gov=raw_gov.strip()	
			gov=raw_gov[:raw_gov.find("-")]
			raw_dep=raw_dep.strip()	
			dep=raw_dep[:raw_dep.find("-")]
			rel=s[:s.find("(")]
			rel.strip()
			#~ print rel,gov,dep,s
			triples.append([rel,gov,dep])
			raw_triples.append([rel,raw_gov,raw_dep])
		
		#~ print triples	
		#~ Find the x relations in prep_x
		f=0
		for rel,raw_gov,raw_dep in raw_triples:
			gov,dep=map(unraw,[raw_gov,raw_dep])
			if rel.startswith("prep_"):
				
				#~ Direct case of a noun preposition noun				
				if pos_dict[gov]==pos_dict[dep]:
					
					#~ Get the spatial relation out from the grammatical relation
					sr = rel[rel.find("prep_")+5:]
					
					#~ Find the list of modifiers adjoining the nouns
					l = find_modifiers(triples, raw_triples,raw_gov)
					
					ro = find_modifiers(triples, raw_triples,raw_dep)
					
					
					#--------------- For gov  -------------------#
				
					# Identifying locatum (l), RO(ro) and spatial relation (sr)
					print " ".join([l,sr,ro])

#~ raw word is as it is mentioned in typed dependencies
#~ 'house-8' is raw, 'house' is unraw
def unraw(raw_word):
	return raw_word[:raw_word.find("-")]
								
#~ Take the set of all typed dependencies for a sentence and return a word with all its modifiers attached in
#~ the order of occurrence in the sentence
""" ASSUMPTION : Finds the modifiers from the triplets where it stays in the gov position """
def find_modifiers (triples, raw_triples, raw_gov):
		
		gov = unraw(raw_gov)
		gov_pos = int(raw_gov[raw_gov.find("-")+1:])
		#~ Find all the triplets where our word occurs at gov position
		result= query_triplet(triples,None,gov,None)
		
		#~ Attach the modifiers in the order they occured in the sentence
		sorted_mods=[]
		mods=[]
		
		#~ raw_gov_word=raw_triples[result[0][1]][GOV_POS]				# Since, result is of the form [  [[rel_r,gov_r,dep_r],tindex] , ... ]
		#~ gov_pos=int(raw_gov_word[raw_gov_word.find("-")+1:])
		
		#~ if gov=="house":
			#~ print result,raw_triples[result[0][1]], raw_gov_word
		for [[rel_r,gov_r,dep_r],tindex] in result:
			if rel_r in modifiers:			
				#~ find the word position of the modifier
				#~ raw_triples[tindex] has the word in raw form
				alpha = raw_triples[tindex][DEP_POS]
				if alpha.startswith(dep_r+"-"):
					dep_r_pos=int(alpha[alpha.find("-")+1:])
					mods.append([dep_r_pos,dep_r])
					
				

		mods.append([gov_pos,gov])											
		mods.sort()
		sorted_mods = map(listGet(1),mods)
		return " ".join(sorted_mods)
		
#~ print len(sentences)
if __name__=="__main__":
	f=open("test.in")
	output_parser(f)

	
