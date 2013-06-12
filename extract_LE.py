from degenerate_LE import extract_degenerate_LEs
from prep_x import *

inp_file = "test.in"
#~ inp_file = "above20desc.in"


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
			return results[0][0][1]
		#~ print results	 
		return get_nsubject(raw_triples, results[0][0][1])
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
			
def verb_mods(raw_triples,prep,raw_dep):
	#~ If pos tag of the 1st result's dep gives a noun, we end the search
	#~ print results
	results=query_triplet_advanced(raw_triples,"prep_"+prep,None,words+"-"+str(word_loc))
	
	#~ print prep,raw_dep,results
	
	#~ for prepositions not of the form "in","on","at" one needs to find the modifiers.
	#~ e.g. 2 minutes from, 3 blocks from, next to
	if len(results)==1:		
		word=results[0][0][1][:results[0][0][1].rfind("-")]
		if not pos_dict[word].startswith("NN"):	
			#~ print "pos tag of prep :",pos_dict[prep]			
			return " ".join(filter(lambda x: True if x!=word else False, find_modifiers(raw_triples,results[0][0][1])))
	return ""
		
	#~ print results	 

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
							le_duet=map(lambda x: x.rsplit("_",3)[0], le.split())
							print " ".join(le_duet)
							continue
							
						
						le_words=map(lambda words : words.rsplit("_",3)[0], le.split())
						
						#~ subject of any of one of the words (except the preposition) in the LE gives you the subject of LE.
						for words_index, words in enumerate(le_words):

							#~ print word,"-",loc_dict[word]
							try:
								#~ print words
								word_loc=get_word_location(loc_dict,words,words_index,le_words)
								
								
								subj = get_subject(pos_dict,raw_triples, prep, words+"-"+str(word_loc))

								#~ print "In LE",le,"subj of ", prep, " and ",words, " is ", subj
								
								#~ print words, word_loc, le_words
								#~ print subj
								if subj!="":
									subj = " ".join(find_modifiers(raw_triples,subj))
									le_duet=map(lambda x: x.rsplit("_",3)[0], le.split())
									if prep not in ["in","at","on"]:
										le_duet[0]=verb_mods(raw_triples, prep, words+"-"+str(word_loc))+ " " +le_duet[0]									
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


