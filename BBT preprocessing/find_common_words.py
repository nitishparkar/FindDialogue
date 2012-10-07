# coding: utf-8

import json
import os
import codecs
import time
from csv_unicode import *
from directories import *


"""
  This script identifies words that occur more than 500 times 
  throughout the series and puts them in a file
  (modified version of index_to_csv.py )
"""


class IndexBuilder():
    """ Generates search index from transcripts """

    index = {}
    not_letters_or_digits = u'!"#%()*+,-./:;<=>?@[\]^_{|}~…“”‘–'
    translate_table = dict((ord(char), ord(' ')) for char in not_letters_or_digits)

    def add_to_dictionary(self, word):
        """
          Eliminates common words & numbers
          If word is present in dictionary, increments count
          otherwise add word to the dictionary with count = 1 
        """
        if len(word) < 3:
            return
        if word.isnumeric():
            return
        if word[0] == '$':
            return
        if word in self.index:
            self.index[word] += 1
        else:
            self.index[word] = 1


    def process_file(self, filename):
        """
          Get individual words from file and
          add them to the dictionary
        """

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
                    if apostrophe_index != -1:
                        # discard letter after apostrophe
                        # so sheldon's becomes sheldon
                        # this may generates weird words like shouldn 
                        # but this tradeoff is acceptable as of now
                        word = word[:apostrophe_index]
                    self.add_to_dictionary(word)
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
    
    # convert index into list
    # list format: [[word, count], ...]
    key_occ = []
    for key in ob.index.keys():
        key_occ.append([key,ob.index[key]])

    # sort the list in descending order of occurrence count
    key_occ.sort(key=lambda occurrence: occurrence[1], reverse=True)

    # generate list of common words
    common_words = []
    for x in key_occ:
        if x[1] < 500:
            break
        common_words.append(x[0])

    # output the list to file
    f_csv = codecs.open("common_words", "w")
    f_csv.write(json.dumps(common_words))
    f_csv.close()

    print "Completed in ", float(time.time() - start_time), " seconds!"

if __name__ == '__main__':
    main()
