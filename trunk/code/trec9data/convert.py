a=1
with open('original_answers') as f:
    while True:
        line1 = f.readline().strip('\n')
        line2 = f.readline().strip('\n')
        line3 = f.readline().strip('\n')
        line4 = f.readline().strip('\n')
        line5 = f.readline().strip('\n')
	print line1,'\t', line2,'\t' ,line3,'\t',line4, '\t',line5
	#if not line6: break
        #print strs[1].strip('\n'), '\t', strs[3]
	#s = f.readline()
	#print s
