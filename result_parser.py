f=open("result_felix.txt")
sentences=""
sent=""
#~ for g_l in g:
	#~ if len(g_l.split())>20:	
		#~ align=0
		#~ for f_l in f:
			#~ if f_l!="\n":
				#~ if align>3:
					#~ sent.append(f_l)
					#~ for nextline in f:
						#~ if nextline=="\n":
							#~ break
						#~ else:
							#~ sent.append(nextline)							
					#~ sentences.append(sent)
					#~ sent=[]
					#~ break
				#~ print f_l.split()[0], 	g_l.split()[:3]
				#~ if f_l.split()[0] in g_l.split()[align]:
					#~ sent.append(f_l)
					#~ align+=1
					#~ continue
				#~ else:
					#~ sent=[]
					#~ align=0
					#~ 
count=0
for f_l in f:
	if f_l!="\n":
		if f_l.split()[0] in [".","'",",","\\","/"]:
			continue
		sent+=(f_l)
		#~ print " adding \n\n", f_l
		count+=1
	else:
		if count>20:
			#~ print count
			#~ print sent
			sentences+=(sent+f_l)
		sent=""	
		count=0
		

print sentences							
