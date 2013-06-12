from copy import deepcopy
from degenerate_LE import extract_degenerate_LEs
from error import MyError 
DEP_POS = 2
GOV_POS = 1
REL_POS = 0

subject_arguments = [
			"nsubj" , # - nominal subject
			"nsubjpass" , # - passive nominal subject
			]

modifiers = [

			"amod" , #  adjectival modifier
			"appos" , #  appositional modifier
			#"advcl" , #  adverbial clause modifier
			"det" , #  determiner
			"predet" , #  predeterminer
			"preconj" , #  preconjunct
			#"infmod" , #  infinitival modifier
			#"mwe" , #  multi, # word expression modifier
			#"mark" , #  marker (word introducing an advcl or ccomp
			"partmod" , #  participial modifier
			"advmod" , #  adverbial modifier
			"neg" , #  negation modifier
			"rcmod" , #  relative clause modifier
			"quantmod" , #  quantifier modifier
			"nn" , #  noun compound modifier
			"npadvmod" , #  noun phrase adverbial modifier
			#"tmod" , #  temporal modifier
			"num" , #  numeric modifier
			"number" , #  element of compound number
			"prep" , #  prepositional modifier
			"poss" , #  possession modifier
			"possessive" , # possessive modifier ('s)
			#"prt" , #  phrasal verb particle
			"dep" , # usual dependent
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

#~ return the set of all triplets that satisfy the provided query of rel,gov,dep
#~ Query search is for those arguments that are set to None
#~ If all are provided, there exists a unique triplet
#~ If atleast one of them is set as None, there can be more than one triplets returned
#~ Finds all queries where rel is contained in the dependency relation. e.g finds prep_far_from, prep_away_from, if provided prep_form
def query_triplet_advanced(t,rel=None,gov=None,dep=None):
	def condition_true(item_l,item_m):
		if (item_l in item_m) or (item_m in item_l) or exceptions(item_l,item_m) or exceptions(item_m,item_l):
			return True
		else:
			return False	
	def equals_advanced(l1,l2):
		if l1==l2:
			return True
		
		elif condition_true(l1[0],l2[0]):
			return equals_advanced(l1[1:],l2[1:])
		
		else:
			return False	
			
	def exceptions(item_l,item_m):
		if item_l==None or item_m==None:
			return False
		if (item_l.startswith("prep_") and item_m.startswith("prep_")):
			if item_l.split("_")[-1]==item_m.split("_")[-1]:
				return True
		return False
				 
		
	def intersect_advanced(l,m):
		intersect=[]
		for item_l in l:
			for item_m in m:
				if item_l==None and item_m==None:
					intersect.append(item_l)
				elif item_l==None or item_m==None:
					continue	
				else:					
					if condition_true(item_m,item_l):						
						intersect.append(item_l if len(item_l) >= len(item_m) else item_m)
		return intersect			 
		
	triplet=[rel,gov,dep]
	out=[]
	
	knowns=filter(is_None,triplet)
	#~ print  t,"####", triplet
	if len(knowns)==0:
		return t
	
	else:
		for tindex, triple in enumerate(t):
			
			#~ Check whether the intersection size is equal to the number of knowns
			if len(intersect_advanced(triple,triplet))==len(knowns):
				#~ if item_l=="prep_from" or item_m=="prep_from":
					#~ print exceptions(item_l,item_m), exceptions(item_m,item_l),item_l,item_m
				
				#~ print "triple",triple,"\t",triplet

				#~ check whether the order is correct for the intersection
				index_set=map(is_None,triplet)
				
				
				temp=[]
				
				for index,value in enumerate(index_set):
					if value==1:
						temp.append(triple[index])
						
				#~ print triple,triplet,knowns,temp
						
				if equals_advanced(temp,knowns):
					out.append([triple,tindex])
		return out
		
		
def output_parser(f):
	sentences=[]
	sentence=""
	count_le = 0 		#number of locative expressions identified
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
			try:
				key,value=tag.split("/")
			except ValueError:
				reverse_index=tag[::-1].find("/")
				index=len(tag)-reverse_index-1
				key,value=tag[:index],tag[index+1:]	
			#~ print key,value
			#~ add_to_pos(key,value)
			pos_dict[key]=value
			loc_dict[key]=counter
			counter+=1
		
		raw_triples = []			#triples with the word postions
		for rel in deps:
			s=rel
			raw_gov,raw_dep=s[s.find("(")+1:s.find(")")].split(",")
			raw_gov=raw_gov.strip()	
			raw_dep=raw_dep.strip()	
			rel=s[:s.find("(")]
			rel.strip()
			raw_triples.append([rel,raw_gov,raw_dep])
		
		#~ print triples	
		#~ Find the x relations in prep_x
		f=0
		for rel,raw_gov,raw_dep in raw_triples:
			gov,dep=map(unraw,[raw_gov,raw_dep])
			#~ print rel , rel.startswith("prep_")
			if rel.startswith("prep_"):
				
				#~ Get the spatial relation out from the grammatical relation
				sr = rel[rel.find("prep_")+5:]
				if 1:
					#--------------- Direct case of a noun preposition noun  -----------------------------#				
					if is_noun(pos_dict[gov]) and is_noun(pos_dict[dep]):
						print ":".join(direct_NN_to_NN(sr, raw_triples, raw_gov, raw_dep))
						
						count_le+=1
					
					
					#---------------- Preposition clause of modifying a verb -------------------------#	
					elif pos_dict[gov].startswith("VB"):
						
						triplets = verb_to_NN(sr, raw_triples, raw_gov, raw_dep)
						if len(triplets)>0:
							count_le+=1
							print ":".join(triplets)
						else:
							print " in --> ",
							print sr,raw_gov,raw_dep
						
						
						
				else:
					print "Error!!!"
					exit
					
					
	print count_le					

#~ Get the nominal subject (nsubj, nsubjpass) of a verb in the dependency titles 
def get_nsubject(raw_triples, raw_gov):
	subjects = []

	for arg in subject_arguments:
		subjects.extend(query_triplet(raw_triples, arg, raw_gov, None))
	
	
	if len(subjects)>1:
		raise MyError("more than one subject to a verb!")
	
	elif len(subjects)==1:
		#~ print subjects
		[rel_r,gov_r,dep_r],tindex = subjects[0]
		raw_nn = raw_triples[tindex][DEP_POS]
		return raw_nn
	else:
		#~ at the dependent position no subject could be found
		#~ the subject of a verb can also be the noun it is modifying.
		#~ so find the nouns getting modified by it.
		subjects.extend(query_triplet(raw_triples, arg, None, raw_gov))
		print raw_gov," modifies ",subjects
		
		# "***subject of the verb couldn't be found***",
		return ""	

	

def direct_NN_to_NN(sr, raw_triples, raw_gov, raw_dep):
	#~ print raw_gov,rel,raw_dep
	
	#~ Find the list of modifiers adjoining the nouns
	l = " ".join(find_modifiers(raw_triples,raw_gov))
	
	
	ro = " ".join(find_modifiers(raw_triples,raw_dep))
	

	
	#--------------- For gov  -------------------#

	# Identifying locatum (l), RO(ro) and spatial relation (sr)
	return [l,sr,ro]

def verb_to_NN(sr, raw_triples, raw_gov, raw_dep):
	subjects = []

	for arg in subject_arguments:
		subjects.extend(query_triplet(raw_triples, arg, raw_gov, None))
	
	
	if len(subjects)>1:
		raise MyError("more than one subject to a verb!")
	
	elif len(subjects)==1:
		#~ print subjects
		[rel_r,gov_r,dep_r],tindex = subjects[0]
		raw_nn = raw_triples[tindex][DEP_POS]
		
		return direct_NN_to_NN (sr, raw_triples, raw_nn, raw_dep)
	else:
		print "***subject of the verb couldn't be found***",
		return []	

#~ raw word is as it is mentioned in typed dependencies
#~ 'house-8' is raw, 'house' is unraw. A general example is 't-intersection-6'
def unraw(raw_word):
	reverse_ind = raw_word[::-1].find("-")
	ind = len(raw_word)-reverse_ind-1
	return raw_word[:ind]
								
#~ Take the set of all typed dependencies for a sentence and return a word with all its modifiers attached in
#~ the order of occurrence in the sentence
""" ASSUMPTION : Finds the modifiers from the triplets where it stays in the gov position """
def find_modifiers (raw_triples, raw_gov):
	def find_modifiers_aux(raw_triples, raw_gov):		
		gov = unraw(raw_gov)
		gov_pos = find_position_in_raw_word(raw_gov)
		#~ Find all the triplets where our word occurs at gov position
		result= query_triplet(raw_triples,None,raw_gov,None)

		#~ Attach the modifiers in the order they occured in the sentence
		sorted_mods=[]
		mods=[]
		
		#~ raw_gov_word=raw_triples[result[0][1]][GOV_POS]				# Since, result is of the form [  [[rel_r,gov_r,dep_r],tindex] , ... ]
		#~ gov_pos=int(raw_gov_word[raw_gov_word.find("-")+1:])
		
		for [[rel_r,gov_r,dep_r],tindex] in result:
			if rel_r in modifiers:			
				#~ find the word position of the modifier
				#~ raw_triples[tindex] has the word in raw form
				alpha = raw_triples[tindex][DEP_POS]
				if alpha.startswith(dep_r):
					dep_r_pos=find_position_in_raw_word(dep_r)
					mods.append([dep_r_pos,unraw(dep_r)])
					
		#~ print raw_gov,gov_pos		
		mods.append([gov_pos,gov])											
		mods.sort()
		#~ print mods, "for ",gov
		#~ sorted_mods = map(listGet(1),mods)
		if len(mods)>1:
			for index,[pos, mod] in enumerate(mods):
				if mod!=gov:
					modlist=find_modifiers_aux(raw_triples,mod+"-"+str(pos))
					try:
						sorted_mods.extend(modlist)
					except:
						print sorted_mods, "**"
						raise	
			#~ map(lambda x: find_modifiers(raw_triples,x), sorted_mods)
		#~ else:
		sorted_mods.append([gov_pos,gov])
		sorted_mods.sort()
				
		return sorted_mods
	
	return map(listGet(1),find_modifiers_aux(raw_triples,raw_gov))

#~ Give 6 from 'house-6' or 1 from 't-intersection-1'
def find_position_in_raw_word(raw_word):
	reverse_ind = raw_word[::-1].find("-")
	ind = len(raw_word)-reverse_ind-1
	word_pos=raw_word[ind+1:]
	try:
		return int(word_pos)
	except ValueError:
		print "Warning: position ", word_pos," for ", raw_word
		return int(word_pos[:-1])					#handles the apostrophe in word position		

def is_noun(word):
	return word.startswith("NN") or word.startswith("PRP")		
#~ print len(sentences)
if __name__=="__main__":
	f=open("test.in")
	#~ print degenerate_LEs()
	output_parser(f)
	
