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
	for line in open('alterunits2.txt'):
        	try:
			sentenceid, tu, au1, au2, au3, au4, au5 = map(str, line.split('\t'))
                	print "TU:",tu , "\n(1)",au1, "\n(2)",au2, "\n(3)",au3, "\n(4)",au4, "\n(5)",au5
			wiki_lookup(tu)
			wiki_lookup(au2.strip(), tu)
			wiki_lookup(au3.strip(), tu)
			wiki_lookup(au4.strip(), tu)
			wiki_lookup(au5.strip(), tu)
		except:
			pass					
def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).lower()




def wiki_lookup(*tu):
	url = 'http://en.wikipedia.org/w/api.php?action=query'
	tu = tu.split(' ')
	if tu != None:
		print ' '.join(tu)
		strings = []
		for i in range(len(tu)):
			for j in range(i+1,len(tu)+1):
				strings.append(' '.join(tu[i:j]))
				strings.append(' '.join(tu[i:j]).title())
		print "Strings generated:",strings, "\n------\n"
		for string in strings:
			string = string.strip('\n')
			if string.find(' ')==-1:
				if string.lower() in ['is','was','the','in','not','be', 'of', 'on', 'a']:
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
					# Iterate thtough all the categories and set flag to true if 
					# the page is a disambiguation page
					if results['query']['pages'][result].has_key('categories'):
						disambig_flag = False
						for category in results['query']['pages'][result]['categories']:
							if category['title'].lower().find('disambiguation') != -1:
								disambig_flag = True
								extract_links(			
					print '%s,%s,%s,%s' % (string.rjust(30),
						results['query']['pages'][result]['title'].rjust(30),
						results['query']['pages'][result]['fullurl'].rjust(60), str(disambig_flag).rjust(15))
								
				#wiki_url = results['query']['pages'][result]['fullurl']
				#wiki_url = url.replace('/wiki/','/wiki/index.php?action=raw&title=')
					
					#reading contents
					#content = urllib.urlopen(wiki_url).read()
					#m = re.search(du,content,re.I)
					#if m is not None: print "Doubt unit found at",m.span()
					
			
			 				#tu[results['query']['pages'][result]['title']] = results['query']['pages'][result]['fullurl']
				

def extract_links():
	dp = 'http://en.wikipedia.org/w/index.php?action=raw&title=Alice'
	import urllib2
	from BeautifulSoup import BeautifulSoup
	
	f = urllib2.urlopen(dp).read()
	soup = BeautifulSoup(f)
	
	wikilink_rx = re.compile(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]')
	
	links = soup.string.splitlines()
	for link in links:
		l = wikilink_rx.sub(r'\1',link)
		if '*' in l:
			print l
	

if __name__ == '__main__':
	#phrase_extraction()
	extract_links()
