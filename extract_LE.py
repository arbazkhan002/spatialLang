from degenerate_LE import extract_degenerate_LEs
from prep_x import *
import sys
#~ inp_file = "test.in"
inp_file = "above20desc.in"


ABLAPTIVES = ["from","of","to"]


#~ Get words of a le. Returns them with ":"  between them
def le_word_get(le):
	le_word=""
	for l in le.split():
		le_word += ":"+l.rsplit("_",3)[0]
	return le_word


def get_prep(le_word):
	first=le_word.split()[0]
	if first[first.rfind("_")+1:]=="PP":
		return first.rsplit(("_"),3)[0]
	else:
		return ""	
	
#~ Find the subject of the dependent in the dependency prep_"prep" (e.g. prep_at)
def get_subject(pos_dict, raw_triples, prep, raw_dep):
	results=query_triplet_advanced(raw_triples,"prep_"+prep,None,raw_dep)
	#~ print prep,raw_dep,results
	if prep=="along":
		pass
		#~ print "************",results,prep,raw_dep,raw_triples
	#~ print results
	if len(results)==1:
		#~ If pos tag of the 1st result's dep gives a noun, we end the search
		word=results[0][0][1][:results[0][0][1].rfind("-")]
		#~ print "******* ", results[0][0][1][:results[0][0][1].rfind("-")], pos_dict[word]
		
		if pos_dict[word].startswith("NN"):
			#~ If the noun has a subj, return the subject, else return the noun
			return results[0][0][1] 
			
		nsubject= get_nsubject(raw_triples, results[0][0][1])					
		#~ print results	 
		return nsubject 
	elif len(results)>1:
		raise MyError("too many subjects for the same prep and dep")
	else:
		return ""	



#~ Gets the location of a word on the basis of the words nearby to it in the locative expression "le_words"
#~ words_index is the index of the word in le_words 
def get_word_location(loc_dict,word,words_index,le_words):
	#~ print word,le_words
	if len(loc_dict[word])==1:
		return loc_dict[word][0]
	elif len(loc_dict[word])>1:
		next_index=(words_index+1)%len(le_words)
		
		while len(loc_dict[le_words[next_index]])>1:
			if next_index==words_index:
				next_index=(next_index+1)%len(le_words)					#for the next step
				break
			next_index=(next_index+1)%len(le_words)
		
			
		#~ Still not sorted out!!!
		if len(loc_dict[le_words[next_index]])>1:			
			for xs in loc_dict[word]:
				for ys in loc_dict[le_words[next_index]]:
					#~ print "xs - ys is ", xs-ys, " with ",loc_dict
					if ((xs-ys) == (words_index - next_index)):
						#~ print word,le_words,xs, "\t ******************** "
						return xs
						
		elif len(loc_dict[le_words[next_index]])==1:
			word_loc=loc_dict[le_words[next_index]][0]-(next_index-words_index)
			#~ if word=="Chetwynd":
				#~ print "I am here", le_words[next_index], loc_dict[le_words[next_index]], word_loc, next_index, words_index

			return word_loc
	
	raise KeyError		

def words_of_LE(le):
	return map(lambda x: x.rsplit("_",3)[0], le.split())

#~ get reference object out from the Locative expression which is accepted in the form of space 
#~ seperated words with format "word_postag_chunktag"
def get_ro(le):
	if len(le.split())==0:
		return ""
	
	if le.split()[0].split("_")[2]!="PP":
		return words_of_LE(le)
	else:
		return get_ro(" ".join(le.split()[1:]))	
		
				
def verb_mods(raw_triples,prep,raw_dep):
	#~ If pos tag of the 1st result's dep gives a noun, we end the search
	#~ print results
	results=query_triplet_advanced(raw_triples,"prep_"+prep,None,words+"-"+str(word_loc))
	
	#~ print prep,raw_dep,results
	
	#~ for prepositions not of the form "in","on","at" one needs to find the modifiers.
	#~ e.g. 2 minutes from, 3 blocks from, next to
	if len(results)==1:		
		word=results[0][0][1][:results[0][0][1].rfind("-")]			#the subject
		if pos_dict[word].startswith("V"):							#only verb modifiers	
			#~ print "pos tag of prep :",pos_dict[prep]			
			#~ print " ", results[0][0][1]
			return " ".join(filter(lambda x: True if x!=word else False, find_modifiers(raw_triples,results[0][0][1])))
	return ""
		
	#~ print results	 

#~  Find all locative expressions linked to this subject
def linked_LE(raw_triples,pos_dict,subj):
	#~ print "linked locativeExprsns to ", subj ," on dep position "
	#~ find dependencies where it occurs in the dep_pos with a prep relation 
	for subj_x in subj.split():
		results=query_triplet_advanced(raw_triples,"prep",None,subj_x)
		#~ print "subj_x: ", subj_x, results
		if len(results)>0:
			break 
		
	#~ for each prepositional relation
	#~ see for the subject of the preposition relation 
	for res in results:
		sr = res[0][0]				#spatial relation
		ro = unraw(res[0][2])				#reference object
		
		#~ print sr,ro, unraw(ro)
		
		if ro!=subj_x:				#from above
			continue
		
		if not sr.startswith("prep"):
			continue
			
		#~ print pos_dict[unraw(res[0][1])]
			
		if is_noun(pos_dict[unraw(res[0][1])]):
			ro1=res[0][1]
			
		#~ a verb definitely 
		else:	
			
			try:
				assert(pos_dict[unraw(res[0][1])].startswith("V"))
				ro1 = get_subject(pos_dict, raw_triples,sr.rsplit("_",2)[1],res[0][2])
			except AssertionError:
				print "/----------------- Assertion Error ---------------------"
				print "startswith ",res[0][1],pos_dict[unraw(res[0][1])] , res
				print "------------------------------------------------------/"
				ro1 = "" 	
		
			#~ print "subject of ",res[0][1],":",ro1
			
		if ro1=="":
			# subject of the verb (almost definitely as nouns would never return empty ro1) couldnt be found
			return "",""
		
		ro1list=find_modifiers(raw_triples,ro1)
		#~ print ro1list
		#~ check for all locative expressions in this description and find the one which matches this ro
		maximum=0
		max_LE=[]
		for locE in desc:
			#~ print "here"
			locE_words=map(lambda words : words.rsplit("_",3)[0], locE.split())		
			
			#~ print set(ro1list) & set(locE_words)
			if len(set(ro1list) & set(locE_words)) >= maximum:
				max_LE=locE
				maximum = len(set(ro1list) & set(locE_words))
		
		if maximum!=0:
			#~ print "LE matching ",ro1, " is ",max_LE		
			noun = " ".join(get_ro(max_LE))
			return noun , sr
	return "", ""
				
		

if __name__=="__main__":
	dge = extract_degenerate_LEs()
	
	f=open(inp_file)
	
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

		counter=1
		orig_sent = []

		for tag in pos:
			try:
				key,value=tag.split("/")
				orig_sent.append(key)
			except ValueError:
				reverse_index=tag[::-1].find("/")
				index=len(tag)-reverse_index-1
				key,value=tag[:index],tag[index+1:]	
				orig_sent.append(key)
			#~ print key,value
			#~ add_to_pos(key,value)
			pos_dict[key]=value
		
			if key not in loc_dict:
				loc_dict[key]=[]
			loc_dict[key].append(counter)
			
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

		#~ print loc_dict
		#~ print 
		#~ print
		#~ print raw_triples
				#~ 
		#~ 
		#~ for desc in dge:
			#~ for le in desc:
				#~ print le
				
		#~ for every sentence check whether it belongs to a LE. If it does, give it a subject		
		for desc in dge:
			for le in desc:
				if le!="":
					le_word=le_word_get(le)
					#~ print le_word#, orig_sent
					#~ See whether this le is in the sentence
					""" Potential error here, there can be differences between the words seperated by Felix and that obtained from stanford parsed '.in' file"""
					if le_word in ":".join(orig_sent): 
						#~ print "true"
						prep = get_prep(le)
						
						#~ print "in le ",le_word, " with prep: ",prep	
						
						if prep=="":
							#~ print " \t A LE STARTING WITHOUT A PREPOSITION ", le
							le_duet=words_of_LE(le)							
							le_string=" ".join(le_duet)
							print le_string
							#~ print linked_LE(raw_triples,pos_dict,le_string)
							continue
							
						
						le_words=map(lambda words : words.rsplit("_",3)[0], le.split())
						
						#~ subject of any of one of the words (except the preposition) in the LE gives you the subject of LE.
						for words_index, words in enumerate(le_words):

							#~ print word,"-",loc_dict[word]
							try:
								#~ print words
								word_loc=get_word_location(loc_dict,words,words_index,le_words)
								
								
								subj = get_subject(pos_dict,raw_triples, prep, words+"-"+str(word_loc))

								#~ print "In LE",le,"subj of prep:", prep, " and dep:",words, " is ", subj
								
								#~ print words, word_loc, le_words
								#~ print subj
								if subj!="":
									subj = " ".join(find_modifiers(raw_triples,subj))
									le_duet=words_of_LE(le)
									#~ print prep
									if prep in ABLAPTIVES:
										extras=verb_mods(raw_triples, prep, words+"-"+str(word_loc))
										
										#~ print "extras:",extras
										le_duet[0]=le_duet[0] if extras=="" else extras+ " " +le_duet[0]									
										
										#~ print le_duet[0]
										#--- ablaptiveLEs -----
							
										#find prep attaching to the subject
										
										#~ print "linked locativeExprsns to ", subj ," on dep position "
										
										
										locE,spatialr= linked_LE(raw_triples,pos_dict,subj)
										
										#~ print locE, spatialr
										if locE!="" and spatialr!="":
											print locE + " " +" ".join(spatialr.split("_")[1:]) + " ", 
										
									print subj," ".join(le_duet)
									break
							#~ else:
							except KeyError as e:
								print "####### error in dictionaries. Felix's word:",e#, " and the dict:\n", loc_dict, pos_dict,le_word
								break
					#~ if prep!="":
						#~ query
						#~ print get_subject(raw_triples, prep, 
						
					#~ get_subject(raw_triples, 
				#~ print "".join(le_word.split())
				#~ break
			#~ break
		#~ break		
	#~ pass


