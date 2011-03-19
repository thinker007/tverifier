import nltk

for line in open('doubtful_statement.txt'):
	a,b,c,d,e,f = map(str, line.split('\t'))
	text1 = nltk.word_tokenize(b)
	text2 = nltk.word_tokenize(c)
	print nltk.pos_tag(text1)
	print nltk.pos_tag(text2)
