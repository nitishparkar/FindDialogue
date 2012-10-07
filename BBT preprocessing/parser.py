import os
import codecs
import time
from directories import *


"""
  This script adds line nos. to all fetched transcripts
  Line nos. are added so while searching,
  focus can be shifted directly to specific line 
  where the word(s) is/are located 
"""


def parse_file(filename):
    """ Adds line number at the beginning of each line """
    
    print 'processing ~\n', filename.decode("ascii", "ignore")

    # http://stackoverflow.com/questions/368805/python-unicodedecodeerror-am-i-misunderstanding-encode
    f_r = codecs.open(fetch_directory + '/' + filename, "r", "utf-8")
    f_w = codecs.open(parse_directory + '/' + filename, "w", "utf-8")
    lineno = 1
    for line in f_r:
        f_w.write(str(lineno) + ' %% ' + line)
        lineno += 1
    f_r.close()
    f_w.close()

def iterate_fetch_directory():
    for dirpath, dirs, files in os.walk(fetch_directory):
        for x in files:
            parse_file(x)

if __name__ == '__main__':
    start_time = time.time()

    iterate_fetch_directory()
    # iterate over vs iterate through:
    # http://stackoverflow.com/questions/2715388/is-it-iterate-through-or-iterate-over-something

    print "All files processed! :)"
    print "Completed in ", float(time.time() - start_time), " seconds!"
