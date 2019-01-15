from urlparse import urlparse
from urlparse import urljoin
import re

# o = urlparse('http://www.cwi.nl:80/%7Eguido/Python.html')
# print o.hostname


# url = 'http://stackoverflow.com/questions/9626535/get-domain-name-from-url'


url =  'asdf http://stackoverflow.com/questions/1234567/blah-blah-blah-blah'

# parts = url.split('//', 1)
# print parts[0]+'//'+parts[1].split('/', 1)[0]

urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)

#print type(urls)
#print type(urls[0])

parsed_uri = urlparse(urls[0])
domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
print domain

