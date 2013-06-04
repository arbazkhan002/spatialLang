f=open("where_db.csv")
cot=0
for line in f:
	line=line.split(":")[7]
	if len(line.split())>20:
		print line
		cot+=1
		
print cot		
