import urllib
import urllib2
import pprint
import json
import sys

key = 'ABQIAAAAEuwUqFVvNIBr6HOzKB5bChSGGgjgYoKsPC_UEFoR883JYNo--hT8ZBr59TKTjdX9ld3fA5qBFkYTuw'

query = 'Barack Obama is'

GOOG_URL = 'https://www.googleapis.com/customsearch/v1?key=AIzaSyAFVODOihDHDoqZS1aDG_xZ2_hCtGKXf7o&cx=017576662512468239146:omuauf_lfve'

def showresults(doubtstmt):
	query = urllib.urlencode({'q':doubtstmt})
	url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query
	#print simplejson.load(urllib.urlopen(url))


	search_response = urllib.urlopen(url)
	search_results = search_response.read()
	search_response_results = json.loads(search_results)
	data = search_response_results['responseData']
	print 'Total results: %s' % data['cursor']['estimatedResultCount']
	hits = data['results']
	print 'Top %d hits:' % len(hits)
	for h in hits: print ' ', h['url']
	print 'For some more results, see %s' % data['cursor']['moreResultsUrl']

#showresults(query)


def customsearch(doubtstmt, **srch_args):
	srch_args.update({
			'q':doubtstmt
			})
	url = GOOG_URL + '&' + urllib.urlencode(srch_args)
	print url
	#url = 	'https://www.googleapis.com/customsearch/v1?key=AIzaSyAFVODOihDHDoqZS1aDG_xZ2_hCtGKXf7o&cx=017576662512468239146:omuauf_lfve&q=lectures' #&callback=handleResponse'
	response = urllib2.urlopen(url)
	data = json.load(response)
	for item in data['items']:
		pprint.PrettyPrinter(indent=4).pprint(item)

customsearch(query)
