iimport urllib
import urllib2
import string
import sys
from BeautifulSoup import BeautifulSoup

user_agent = 'Mozilla/5 (Solaris 10) Gecko'
headers = { 'User-Agent' : user_agent }

values = {'s' : sys.argv[1] }
data = urllib.urlencode(values)
request = urllib2.Request("http://www.answers.com/", data, headers)
response = urllib2.urlopen(request)
print response

