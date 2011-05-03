import sys

def process_sentences(fname):
	f = open(fname,"r")
	for line in f :
		coloumns = line.split("\t")
		wf=open("sentences/"+coloumns[0],"w")
		wf.write(line)
		wf.close()
		
process_sentences(sys.argv[1])