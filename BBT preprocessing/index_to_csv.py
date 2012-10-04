# coding: utf-8

import json
import os
import codecs
import time
from csv_unicode import *
from directories import *

"""
  This script generates search index from transcripts and
  writes it to a csv file required by the GAE bulkloader
  Index format: 
    word1 : [[season, episode, lineno], [season, episode, lineno], ...],
    word2 : [[season, episode, lineno], [season, episode, lineno], ...]
  Before writing to csv file, list is converted to json string
"""


class IndexBuilder():
    """ Generates search index from transcripts """

    index = {}
    not_letters_or_digits = u'!"#%()*+,-./:;<=>?@[\]^_{|}~…“”‘–'
    translate_table = dict((ord(char), ord(' ')) for char in not_letters_or_digits)

    def add_to_dictionary(self, word, occurrence):
        """
          Eliminates common words & numbers
          adds word occurrence to the dictionary
        """
        if len(word) < 3:
            return
        if word.isnumeric():
            return
        if word[0] == '$':
            return
        if word in self.index:
            self.index[word].append(occurrence)
        else:
            self.index[word] = [occurrence]


    def process_file(self, filename):
        """
          Get individual words from file and
          add them to the dictionary
        """

        si = filename.find('Series')
        season = int(filename[si+7:si+8])
        ei = filename.find('Episode')
        episode = int(filename[ei+8:ei+10])
        #print "S", season, "E", episode

        # should have used fetch_directory
        f = codecs.open(parse_directory + '/' + filename, "r", "utf-8")

        for line in f:
            lineno, linetext = line.split(' %% ')
            colon_index = linetext.find(':')
            if colon_index != -1:
                linetext = linetext[colon_index+1:]

            # remove unwanted unicode symbols
            linetext = linetext.translate(self.translate_table)

            words = linetext.split(' ')
            for word in words:
                word = word.strip()
                if word:
                    word = word.lower()
                    apostrophe_index = word.find(u"\u2019")
                    lst = [season, episode, int(lineno)]
                    if apostrophe_index != -1:
                        # discard letter after apostrophe
                        # so can't becomes can
                        # this may generates weird words like shouldn 
                        # but this tradeoff is acceptable as of now
                        word = word[:apostrophe_index]
                    self.add_to_dictionary(word, lst)
        f.close()   

    def iterate_parse_directory(self):
        for dirpath, dirs, files in os.walk(parse_directory):
            for x in files:
                self.process_file(x)
                print "processing: ", x
        print "All episodes loaded in index! :)"


def main():
    start_time = time.time()

    # build index
    ob = IndexBuilder()
    ob.iterate_parse_directory()

    print "total keys", len(ob.index)
    print "sorting and eliminating duplicates..."

    # sort word occurences and eliminate duplicates
    # i.e. word occurring more than once on the same line
    for key in ob.index.keys():
        ob.index[key].sort()
        # duplication elimination code from Python docs
        last = ob.index[key][-1]
        for i in range(len(ob.index[key])-2, -1, -1):
            if last == ob.index[key][i]:
                del ob.index[key][i]
            else:
                last = ob.index[key][i]

    print "generating csv..."
    f_csv = open("search_index.csv", "w") # Don't use utf-8, causes csv writer to crash
    uw = UnicodeWriter(f_csv)
    uw.writerow(['word', 'occurrences']) # header line
    for x in ob.index.keys():
        uw.writerow([x, json.dumps(ob.index[x])])
    f_csv.close()
    print "Index exported to search_index.csv"
    print "Completed in ", float(time.time() - start_time), " seconds!"

if __name__ == '__main__':
    main()
