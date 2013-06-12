f=open("/home/arbazk/MTT/UniMelb/Code/Dependencies exploitation/gitStore/result_felix_above20.txt")

for line in f:
	l=line.split()
	if len(l)>1:
		if l[11]=="PP":
			print l[0]
