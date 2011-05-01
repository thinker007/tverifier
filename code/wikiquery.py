from __future__ import division
import nltk
from nltk.corpus import stopwords
import urllib
import pprint
import simplejson
import re
import itertools

url = 'http://en.wikipedia.org/w/api.php?action=list'
#
debug = True
#regex_tokenize = True
regex_tokenize = False
def stop_removed():
	stopset = set(stopwords.words('english'))
	
	sentences = {}
	with open('DU_TU.5.txt') as f:
		for line in f:			
			du = line.split('\t')[0]
	    		tu = line.split('\t')[1]
			#print du, tu
			tu_stop_removed = ''
	        	for word in tu.split(' '):
	            		if word not in stopset:
	                		tu_stop_removed +=word.strip('\n')+' '
			sentences.update({du:tu_stop_removed}) 
#	print sentences
	return sentences

def wikisearch():
	topic_units = stop_removed()
	for doubt_unit, topic_unit in topic_units.iteritems():
	 	print doubt_unit,';',topic_unit.rstrip("\n")
		


#http://en.wikipedia.org/w/api.php?
#action=query
#&list=search
#&srprop=size|wordcount|timestamp|score|snippet|titlesnippet|redirecttitle|redirectsnippet|sectiontitle|sectionsnippet|hasrelated
#&srsearch=SEARCH STRING GOES HERE
#srwhat=text|title|nearsearch (only one value is allowed)
#
#&format=json
#
		url = 'http://en.wikipedia.org/w/api.php?action=query&list=search'
		srch_args = {'format':'json',
		      #'srprop':'size|wordcount|timestamp|score|snippet|titlesnippet|redirecttitle|redirectsnippet|sectiontitle|sectionsnippet|hasrelated',
		      'srprop':'titlesnippet|snippet',
			'srsearch':doubt_unit,
			'srwhat':'text',	
			}
		url_srch = url + '&' + urllib.urlencode(srch_args)
		#print url_srch
		results = simplejson.load(urllib.urlopen(url_srch))
		if debug:
			pprint.PrettyPrinter(indent=4).pprint(results)

		for result in results['query'].get('search',()):
			#SNIPPETS
			#TODO include distance between matches in the weight
			snippet_split_weights = {}
			snippet_splits = re.split(r'<b>...</b>',result['snippet'] )
			for snippet_split in snippet_splits:
				snippet_split_len = len(snippet_split)
				snippet_split_match_count = len(re.findall(r'<span class=\'searchmatch\'>\w+</span>',snippet_split))
				snippet_split_weights[snippet_splits.index(snippet_split)] = snippet_split_match_count/snippet_split_len
			snippet_weight = 0
			for snippet_split_weight in snippet_split_weights.values():
				snippet_weight +=snippet_split_weight
			snippet_weight= 0.33*snippet_weight			
			
			#TITLE
			title_match_count = len(re.findall(r'<span class=\'searchmatch\'>\w+<\/span>',result['titlesnippet']))
			title_len = len(result['title'])
			title_weight = title_match_count/title_len

			#TODO need to determine appropriate wieghts
			overall_result_weight = (title_weight+snippet_weight)/2
			
			#print '\t',snippets_splits.encode("utf-8")

			snippet = re.sub(r'<.*?>','',result['snippet'])
			
			if regex_tokenize:
				from nltk.tokenize import RegexpTokenizer
        			tokenizer = RegexpTokenizer('([A-Z]\.)+|\w+|\$[\d\.]+')
			
				snippet_tokens = set(tokenizer.tokenize(snippet))
				title_tokens = set(tokenizer.tokenize(result['title']))
				topic_unit_tokens = set(tokenizer.tokenize(doubt_unit))
			else:
				snippet_tokens = set((snippet).lower().split(' '))
				title_tokens = set((result['title']).lower().split(' '))
				topic_unit_tokens = set(doubt_unit.lower().split(' '))

				
			found = False
			
			if snippet_tokens.intersection(topic_unit_tokens):
				print "S",';',title_weight,';',snippet_weight,';',overall_result_weight 
				found = True
			if title_tokens.intersection(topic_unit_tokens):
				print "T",';',title_weight,';',snippet_weight,';',overall_result_weight
				found = True
			if found == False:
				print "N",';',title_weight,';',snippet_weight,';',overall_result_weight
   		print "="*50	

def rte_features(rtepair):
    extractor = nltk.RTEFeatureExtractor(rtepair)
    features = {}
    features['word_overlap'] = len(extractor.overlap('word'))
    features['word_hyp_extra'] = len(extractor.hyp_extra('word'))
    features['ne_overlap'] = len(extractor.overlap('ne'))
    features['ne_hyp_extra'] = len(extractor.hyp_extra('ne'))
    return features


def POS_tag():
	for line in open('DU_TU.5.txt'):
	        a,b = map(str, line.split('\t'))
	        text1 = nltk.word_tokenize(a)
	        text2 = nltk.word_tokenize(b)
	        print nltk.pos_tag(text1)
	        print nltk.pos_tag(text2)

def phrase_extraction():
	#wikisearch()
	url = 'http://en.wikipedia.org/w/api.php?action=query'

	 with open('alter_units.txt') as f:
	        while True:
			try:
				sentenceid, tu, au = map(str, f.readline().split('\t'))
				if sentenceid == prev_sentenceid:
					au_list.append(au)
				else:
					prev_sentenceid = sentenceid
					au_list = [au]
			except:
				
		tu = tu.split(' ')
		if tu != None:
			print ' '.join(tu)
			strings = []
			for i in range(len(tu)):
				for j in range(i+1,len(tu)+1):
					strings.append(' '.join(tu[i:j]))
			#print "Strings generated:",strings, "\n------\n"
			for string in strings:
				string = string.strip('\n')
				if string.find(' ')==-1:
					if string in ['is','was','the','in','not','be', 'of', 'on']:
						continue
				srch_args = {'format':'json',
		   					'inprop':'displaytitle|url',
							'titles':string,
							'prop':'info|categories',
							'redirects':'',	
							}
				url_srch = url + '&' + urllib.urlencode(srch_args)
				results = simplejson.load(urllib.urlopen(url_srch))
				
				for result in results['query']['pages']:
					if int(result)>-1:
						print '%s,%s,%s' % (string.rjust(30) ,
							results['query']['pages'][result]['title'].rjust(30),
							results['query']['pages'][result]['fullurl'].rjust(50))
						wiki_url = results['query']['pages'][result]['fullurl']
						wiki_url = url.replace('/wiki/','/wiki/index.php?action=raw&title=')
						
						#reading contents
						#content = urllib.urlopen(wiki_url).read()
						#m = re.search(du,content,re.I)
						#if m is not None: print "Doubt unit found at",m.span()
						
						# query for categories
						#if results['query']['pages'][result].has_key('categories'):
						#	for category in results['query']['pages'][result]['categories']:
								#print category['title']
							
		 				tu[results['query']['pages'][result]['title']]= results['query']['pages'][result]['fullurl']
						

if __name__ == '__main__':
	phrase_extraction()
