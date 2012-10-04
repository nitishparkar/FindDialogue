import urllib
import time
import codecs
from bs4 import BeautifulSoup
from directories import *

"""
  This script fetches all the episodes of Big Bang Theory from
 	http://bigbangtrans.wordpress.com/
  and puts them in a directory
"""

def put_in_file(content):
	""" Put fetched transcript in a file """
	exclude_min = 0
	exclude_max = len(content)

	# every transcript starts with 'Scene'
	i = content.find('Scene')
	if i != -1:
		exclude_min = i 

	exclude_terms = ['Teleplay: ', 'Story: ', 'Written by Chuck', 'Like this:', 'You can start editing here']
	# common terms at the end of transcripts
	# noise for my purpose
	
	for x in exclude_terms:
		i = content.find(x)
		if i != -1:
			exclude_max = min(exclude_max, i)
	
	# Determine the name of output file
	fn_start = content.find('Series')
	fn_end = content.find('\n', fn_start)
	if fn_start != -1 and fn_end != -1:
		filename = content[fn_start:fn_end] + ".txt"
	else:
		filename = "foo.txt"
		print "Argh! Anomaly"

	print 'writing fetched content to ~\n', filename.encode('ascii', 'ignore')	

	file_object = codecs.open("./" + fetch_directory + "/" + filename, "w", "utf-8")
	
	# eliminate extra infromation such as title and credits.
	file_object.write(content[exclude_min:exclude_max]) 
	
	file_object.close()


def get_page(url):
	""" Just a wrapper """
	try:
		return urllib.urlopen(url).read()
	except:
		return ""

def get_all_episode_urls():
	""" Returns the urls of transcripts of all episodes """
	
	seed_page = get_page("http://bigbangtrans.wordpress.com/about/")
	url_list = []
	list_index = 0
	anchor_index = 0
	anchor_end_index = 0

	"""
	 all links to Big Bang Theory episode transcripts have following structure:
		<li class="page_item page-item-3 current_page_item">
			<a href="http://bigbangtrans.wordpress.com/series-1-episode-1-pilot-episode/">
			Series 1 Episode 01 - Pilot Episode</a>
		</li>
	""" 

	while True:
		list_index = seed_page.find('<li class="page_item page-item-', list_index + 1)
		if list_index == -1:
			break
		anchor_index = seed_page.find('<a href=', list_index)
		anchor_end_index = seed_page.find('">', anchor_index)
		page_url = seed_page[anchor_index+9:anchor_end_index]
		if page_url.find('/about/') >= 0:
			print 'About page eliminated!'
			continue
		url_list.append(page_url)
	
	return url_list


def main():
	start_time = time.time()

	url_list = get_all_episode_urls()
	print 'Total no. of episodes to be fetched: ', len(url_list)

	for x in url_list:
		print '-' * 75
		print 'fetching content from:\n', x
		c = get_page(x)
		b = BeautifulSoup(c)
		txt = b.find('div', id='content').get_text() # get transscipt from blog post
		put_in_file(txt)

	print "Completed in ", int(time.time() - start_time), " seconds!"

if __name__ == '__main__':
	main()