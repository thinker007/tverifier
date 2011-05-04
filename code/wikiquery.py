from __future__ import division
import nltk
from nltk.corpus import stopwords
import urllib
import pprint
import simplejson
import re
import itertools
import traceback
import urllib2
from BeautifulSoup import BeautifulSoup
import string
	

url = 'http://en.wikipedia.org/w/api.php?action=list'
#
debug = False
#debug = True
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
                	print "Topic unit is:",tu 
			print "Find articles from Topic unit:"
			tu_dict = wiki_lookup_tu(tu)
			print "Find articles from Alternate unit:"
			print "Alternate units are:", "\n(1)",au1, "\n(2)",au2, "\n(3)",au3, "\n(4)",au4, "\n(5)",au5
			print '%s %s %s %s' % ('Shingle'.rjust(30),'Article Title'.rjust(30),'URL'.rjust(60),'Disambiguation'.rjust(15))	
			print '-'*150
	
			au_dict = {}
	
			au_dict.update(wiki_lookup_au(au1.strip(), tu))
			au_dict.update(wiki_lookup_au(au2.strip(), tu))
			au_dict.update(wiki_lookup_au(au3.strip(), tu))
			au_dict.update(wiki_lookup_au(au4.strip(), tu))
			au_dict.update(wiki_lookup_au(au5.strip(), tu))
			
			outputfn = 'output_alg1/'+sentenceid
			fp = open(outputfn,'wb')
			fp.write(tu+'\n')

			print '='*150
			print 'Final Matrix'.rjust(75)
			print '='*150

		
			print '\t\t\t','\t\t'.join(tu_dict.keys())


			if debug:	
				for au_title, au_url in au_dict.items():
					print  au_title
					score = []
					for tu_title, tu_url in tu_dict.items():
						relevant_words = string_diff(tu.split(' '),tu_title)
						if len(au_url)>0 and len(tu_url)>0:	 
							score.append(count_intersect(au_url,tu_url,relevant_words))
					print '\t\t','\t'.join(score)
			else:
				for au_title, au_url in au_dict.items():
					score =0
					for tu_title, tu_url in tu_dict.items():
						relevant_words = string_diff(tu.split(' '),tu_title)
						if len(au_url)>0 and len(tu_url)>0:
							score+=count_intersect(au_url,tu_url,relevant_words)
					
					print score, au_title
					au_score = str(score) + ' ' + au_title + '\n'
					fp.write(au_score)
		except:
			#print traceback.print_stack()		
			print 'Some error'			



def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).lower()



def wiki_lookup_au(*args):
	url = 'http://en.wikipedia.org/w/api.php?action=query'
	unit = args[0]
	if len(unit)>1:
		unit = unit.title()
	topic_unit = args[1].split(' ')
	#print unit, ' '.join(topic_unit)
	unit_dict = {'':''}
	srch_args = {'format':'json',
			'inprop':'displaytitle|url',
			'titles':unit,
			'prop':'info|categories',
			'redirects':'',	
			}
	url_srch = url + '&' + urllib.urlencode(srch_args)
	results = simplejson.load(urllib.urlopen(url_srch))
	
	wiki_title = ''
	wiki_url_raw = ''	
	for result in results['query']['pages']:
		if int(result)>-1:
		# Iterate thtough all the categories and set flag to true if 
		# the page is a disambiguation page
			if results['query']['pages'][result].has_key('categories'):
				disambig_flag = False
				for category in results['query']['pages'][result]['categories']:
					if category['title'].lower().find('disambiguation') != -1:
						disambig_flag = True
				
			print '%s,%s,%s,%s' % (unit.rjust(30),
				results['query']['pages'][result]['title'].rjust(30),
				results['query']['pages'][result]['fullurl'].rjust(60), str(disambig_flag).rjust(15))
								
					
			wiki_url = results['query']['pages'][result]['fullurl']
			wiki_url_raw = wiki_url.replace('/wiki/','/w/index.php?action=raw&title=')
				
			wiki_title = results['query']['pages'][result]['title']
	
			if disambig_flag is True:
				#Check if this is only the topic unit
				print '-'*150
				print "\n\tGot a disambiguation article. Trying to find relevant one"
				print "\tVisiting", wiki_url_raw, "to disambiguate."
				wiki_url_raw = extract_links(wiki_url_raw, topic_unit)

				#print 'Got the disambiguated url',wiki_url_raw	

	return {wiki_title:wiki_url_raw}	




def wiki_lookup_tu(*args):
	url = 'http://en.wikipedia.org/w/api.php?action=query'
	if len(args)==2:
		topic_unit = args[1]
	unit = args[0]

	unit = unit.split(' ')
	if unit != None:
		#print ' '.join(tu)
		strings = []
		for i in range(len(unit)):
			for j in range(i+1,len(unit)+1):
				strings.append(' '.join(unit[i:j]))
				strings.append(' '.join(unit[i:j]).title())
		print "Shingles generated from the topic unit:\n",strings, "\n------\n"
		print '%s %s %s %s' % ('Shingle'.rjust(30),'Article Title'.rjust(30),'URL'.rjust(60),'Disambiguation'.rjust(15))	
		print '-'*150

		unit_dict = {}
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
				
					print '%s,%s,%s,%s' % (string.rjust(30),
						results['query']['pages'][result]['title'].rjust(30),
						results['query']['pages'][result]['fullurl'].rjust(60), str(disambig_flag).rjust(15))
								
					
					wiki_url = results['query']['pages'][result]['fullurl']
					wiki_url_raw = wiki_url.replace('/wiki/','/w/index.php?action=raw&title=')
				
	
					if disambig_flag is True:
						#Check if this is only the topic unit
						print '-'*150
						print "\n\tGot a disambiguation article. Trying to find relevant one"
						print "\tVisiting", wiki_url_raw, "to disambiguate."
						if len(args) == 1:
							unit_minus_string = string_diff(unit,string)
							print '\tWill use rest of the terms in the topic unit, i.e.\"',' '.join(unit_minus_string), '\" to disambiguate'
							wiki_url_raw = extract_links(wiki_url_raw, unit_minus_string)
						else:
							print 'TU sent with AU:'
							print  type(args[1].split(' '))
							wiki_url_raw = extract_links(wiki_url_raw, args[1].split(' '))
					
					wiki_title = results['query']['pages'][result]['title']
					
					try:
						unit_dict[wiki_title]=wiki_url_raw
					except:
						print "Pass"		
					#reading contents
					#content = urllib.urlopen(wiki_url).read()
					#m = re.search(du,content,re.I)
					#if m is not None: print "Doubt unit found at",m.span()
					
			
			 				#tu[results['query']['pages'][result]['title']] = results['query']['pages'][result]['fullurl']
					
		for title, url in unit_dict.items():
			print title, url
		return unit_dict

def string_diff(stringa, stringb):
	# First argument is a list second argument is a string
	#print 'In the string diff',stringa, stringb, '\n'
	listb = stringb.split(' ')
	for word in listb:
		if word.lower() in stringa:
			stringa.remove(word.lower())
			#print stringa
	#print "Returning from string_diff",stringa, '\n\n'
	return stringa	
	
			
def count_intersect(wiki_url_raw1, wiki_url_raw2, relevant_words):
		 
	#print 'TU_URL:', wiki_url_raw1 
	#print 'AU_URL:',wiki_url_raw2
	#print 'Rest of the words:' ,' '.join(relevant_words)	
	trans = string.maketrans("[]*","   ")
	f1 = urllib2.urlopen(wiki_url_raw1).read()
	f2 = urllib2.urlopen(wiki_url_raw2).read()
	soup1 = BeautifulSoup(f1)
	soup2 = BeautifulSoup(f2)
	wikilink_rx = re.compile(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]')

	bag_of_words1 = wikilink_rx.sub(r'\1',str(soup1)).lower().split()
	bag_of_words2 = wikilink_rx.sub(r'\1',str(soup2)).lower().split()
	#relevant_words = set(relevant_words)

	bow_freq1 = {}
	bow_freq2 = {}
	bow_freq3 = {}	
	for word in bag_of_words1:
		try:
			bow_freq1[word] += 1
		except:
			bow_freq1[word] = 1
	for word in bag_of_words2:
		try:
			bow_freq2[word] += 1
		except:
			bow_freq2[word] = 1
	for k in bow_freq1:
		if bow_freq2.get(k,0)>	0:
			bow_freq3[k] = bow_freq1[k] + bow_freq2[k]

	if debug:
		score = ''	
		for word in relevant_words:
			if bow_freq3.get(word,0) > 0 and word not in ['the','a']:
	 			score += word + '('+ str(bow_freq3.get(word)) + '),'
		return score 
	else:
		score = 0
		for word in relevant_words:
			if bow_freq3.get(word,0) > 0 and word not in ['the', 'a']:
				score+=bow_freq3.get(word)
	 	return score	

def extract_links(wiki_url_raw, relevant_words):
	url_front = 'http://en.wikipedia.org/w/index.php?action=raw&title='
		#print wiki_url_raw, relevant_words	
	trans = string.maketrans("[]*","   ")
	f = urllib2.urlopen(wiki_url_raw).read()
	soup = BeautifulSoup(f)
	wikilink_rx = re.compile(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]')

	links = str(soup).splitlines()
	relevant_words = set(relevant_words)
	
	print "\n\tThe options are:"
	
	
	max_count = 0
	disambig_url = ''
	for link in links:
		l = wikilink_rx.sub(r'\1',link)
		if '*' in l:
			print '\t',l
			set_l = set(l.lower().split())
			count = len(set_l.intersection(relevant_words))
			if count > max_count:
				max_count = count
				# split by comma, take the first element,
				# split by |, take the first element
				# this is the title of the wikiarticle
				# strip the surrounding spaces
				# replace iniside spaces with underscore 
				link = link.split(',')[0].split('|')[0].encode("utf-8").translate(trans).strip(' ').replace(' ','_')
				disambig_url = link
				
	if max_count == 0:
		print "\n\tNone of the articles are related to the topic unit" 
		print '-'*150
		# TODO Return none
		return wiki_url_raw
	else:
		print "\n\tMost related topic unit seems to be:", url_front + disambig_url
		print '-'*150
		return url_front + disambig_url
	

if __name__ == '__main__':
	phrase_extraction()
	#extract_links()
