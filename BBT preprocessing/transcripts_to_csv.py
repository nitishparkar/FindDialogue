# coding: utf-8

import json
import os
import codecs
import time
from csv_unicode import *
from directories import *


"""
  This script generates a csv file of transcripts 
  required by the GAE bulkloader
  format of csv file:
    show, title, transcript
"""

uw = None

def load_transcripts(filename):
    global uw

    # generate show (season + episode) and title from transcript
    si = filename.find('Series')
    season = filename[si+7:si+8]
    ei = filename.find('Episode')
    episode = filename[ei+8:ei+10]
    show = season + episode
    tsi = filename.find(u'\u2013') # unicode en dash –
    tei = filename.find('.txt')
    title = filename[tsi+2:tei].replace(u'\u00A0', ' ') # Unicode Character 'NO-BREAK SPACE'

    f = codecs.open(parse_directory + '/' + filename, 'r', 'utf-8')
    transcript = f.read()
    uw.writerow([show , title, transcript])
    f.close()

def iterate_parse_directory():
    for dirpath, dirs, files in os.walk(unicode(parse_directory)):
        for x in files:
            print "processing: ", x.encode('ascii', 'ignore')
            load_transcripts(x)
    print "All episodes' transcripts loaded! :)"

def main():
    global uw
    start_time = time.time()

    f_csv = open("transcripts2.csv", "w")
    uw = UnicodeWriter(f_csv)
    uw.writerow(['show', 'title', 'transcript']) # header line
    iterate_parse_directory() # content lines
    f_csv.close()
    
    print "Index exported to transcripts2.csv"
    print "Completed in ", float(time.time() - start_time), " seconds!"

if __name__ == '__main__':
    main()