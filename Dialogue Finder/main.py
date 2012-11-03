# coding: utf-8

import webapp2
import os
import jinja2
import logging
import json
import math
import re
from google.appengine.api import memcache
from models import *

# runs in debug mode only on dev server
DEBUG = os.environ['SERVER_SOFTWARE'].startswith('Dev')

""" Jinja2 """
jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), './templates')))


def nl2br(value): 
    return value.replace('\n','<br/>')

def mark_words(text, words):
    for word in words.split(' '):
        text = re.sub(word, '<mark>' + word + '</mark>', text, flags=re.IGNORECASE)
        #text = text.replace(word,'<b>' + word + '</b>')
    return text

jinja_environment.filters['nl2br'] = nl2br
jinja_environment.filters['mark_words'] = mark_words


class HomeHandler(webapp2.RequestHandler):
    """ Handler for / """
    def get(self):
        template = jinja_environment.get_template('home.htm')
        self.response.out.write(template.render())


class SearchHandler(webapp2.RequestHandler):
    """ Handler for /search """

    def my_renderer(self, **parameters):
        template = jinja_environment.get_template('search.htm')
        self.response.out.write(template.render(parameters))    

    def query_filter(self, query, max_words=10):
        """ 
          Removes numbers and common words from query, 
          truncates strings with single quote,
          eliminates some unicode punctuation symbols
          and if query contains more than max_words words, discards them
          returns a list valid words from search query
        """
        common_words = ["you", "the", "and", "that", "what", "have", "with", "not", 
        "your", "for", "this", "are", "don", "just", "know", "can", "sheldon", "was", 
        "but", "well", "leonard", "okay", "all", "like", "out", "about", "going", 
          "yeah", "right", "there", "she", "get", "one", "how", "here", "her", "they", 
          "want", "why", "good", "now", "him", "would", "think", "did", "when", "his", 
          "hey", "knock", "see", "got", "really", "let", "from", "come", "howard", 
          "yes", "who", "apartment", "time", "little", "look", "penny", "back"]
        
        not_letters_or_digits = u'!"#%()*+,-./:;<=>?@[\]$^_’{|}~…“”‘–'
        translate_table = dict((ord(char), ord(' ')) for char in not_letters_or_digits)
        query = query.translate(translate_table)
        
        filtered_words = query.split()
        for i in range(len(filtered_words)-1, -1, -1):
            if len(filtered_words[i]) < 3 or filtered_words[i].isnumeric():
                del filtered_words[i]
            else:
                apostrophe_index = filtered_words[i].find("'")
                if apostrophe_index != -1: 
                    filtered_words[i] = filtered_words[i][:apostrophe_index]
        
        ret = []
        for x in filtered_words:
            if x not in common_words:
                ret.append(x)
            if len(ret) >= max_words:
                break
        return ret

    def process_filtered_query(self, filtered_words, limit=10):
        """
          Core search logic 
          Returns a list of results sorted by relevance
          limit determines max. no. of results returned
        """
        model_instances = BBTIndex.get_by_key_name(filtered_words)
        model_instances = [l for l in model_instances if l is not None]

        #print "Initial Lists:"
        #for x in model_instances:
        #    print x.word, ':', x.occurrences
        
        if len(model_instances) < 1:
            #print "invlid len"
            return []
        
        meta_list = json.loads(model_instances[0].occurrences)
        for x in meta_list:
            x.append(5)
        
        #print 'ml', meta_list
        for i in range(1, len(model_instances)):
            #print "outer loop i", i
            for occurrence in json.loads(model_instances[i].occurrences):
                #print "inner loop", occurrence
                occurrence.append(5)
                x = 0
                while x < len(meta_list):
                    #print 'xmeta:',meta_list
                    if meta_list[x][0] == occurrence[0] and meta_list[x][1] == occurrence[1] and meta_list[x][2] == occurrence[2]:
                        meta_list[x][3] += 10
                        break
                    if meta_list[x][0] == occurrence[0] and meta_list[x][1] == occurrence[1] and meta_list[x][2] > occurrence[2]:
                        meta_list.insert(x, occurrence)
                        break
                    if meta_list[x][0] == occurrence[0] and meta_list[x][1] > occurrence[1]:
                        meta_list.insert(x, occurrence)
                        break
                    if meta_list[x][0] > occurrence[0]:
                        meta_list.insert(x, occurrence)
                        break
                    x += 1
                else:
                    meta_list.append(occurrence)
        #print "Duplicates combined!", meta_list
        
        new_meta_list = []
        combined = False
        for x in range(1, len(meta_list)):
            if meta_list[x-1][0] == meta_list[x][0] and meta_list[x-1][1] == meta_list[x][1] and math.fabs(meta_list[x-1][2]-meta_list[x][2]) < 3:
                new_meta_list.append(meta_list[x][:])
                new_meta_list[-1][2] = (meta_list[x-1][2] + meta_list[x][2])/2
                new_meta_list[-1][3] = meta_list[x-1][3] + meta_list[x][3]
                combined = True            
            else:
                if not combined:
                    new_meta_list.append(meta_list[x-1])
                combined = False
            #print "new x:",x,new_meta_list
                
        if not combined:
            new_meta_list.append(meta_list[-1])    
        #print "Neighbours Combined!", new_meta_list
        
        # sorting reference: Python docs
        new_meta_list.sort(key=lambda occurrence: occurrence[3], reverse=True)
        return new_meta_list[:limit]

    def get_snippet_from_transcript(self, transcript, lineno):
        """
          Eliminates line numbers and returns dialogue snippet
          A snippet consists of 3 lines(max) - the line which contains results
          and a line before and after it.
        """
        snippet = ""
        start = max(lineno - 1, 0)
        start_index = transcript.find(str(start) + " %%")
        if start_index == -1:
            return snippet
        end_index = transcript.find(str(lineno+2) + " %%")
        if end_index == -1:
            snippet = transcript[start_index:]
        else:
            snippet = transcript[start_index:end_index]

        reg_res = re.split(r'^[0-9]+ %%', snippet, flags=re.MULTILINE)
        filtered_snippet = ''.join(reg_res[1:])
        return filtered_snippet

    def fetch_results(self, qlist):
        """
          For each result returned by process_filtered_query() 
          gets dialogue snippet from transcript
        """
        results = []
        for x in qlist:
            memcache_index = str(x[0] * 100 + x[1])
            title = None
            snippet = None
            cached_transcript = memcache.get(memcache_index)
            if cached_transcript:
                title = cached_transcript[0]
                snippet = self.get_snippet_from_transcript(cached_transcript[1], x[2])
            else:
                show = BigBangTheory.get_by_key_name(memcache_index)
                if show:
                    title = show.title
                    transcript = show.transcript
                    snippet = self.get_snippet_from_transcript(transcript, x[2])
                    memcache.set(memcache_index, [title, transcript])
            if snippet and title:
                results.append([x[0], x[1], title, snippet, x[2], x[3]])
        return results

    def get(self):
        results = None

        query = self.request.get('q').strip()
        if len(query) == 0:
            self.my_renderer(filtered_query='')
            return

        lowercase_query = query.lower()
        logging.info(query) 
        
        filtered_words = self.query_filter(lowercase_query)
        if len(filtered_words) == 0: # After filtering all words were eliminated
            self.my_renderer(query=query, filtered_query='')
            return
        
        qlist = self.process_filtered_query(filtered_words)
        if len(qlist) == 0: # No results found
            self.my_renderer(query=query, filtered_query=' '.join(filtered_words))
            return

        results = self.fetch_results(qlist)
        self.my_renderer(query=query, filtered_query=' '.join(filtered_words), results=results)


class ViewHandler(webapp2.RequestHandler):
    """ Handler for /view """

    def my_renderer(self, **parameters):
        template = jinja_environment.get_template('view.htm')
        self.response.out.write(template.render(parameters)) 

    def get_img_tag(self, character):
        if 'sheldon' in character.lower():
            return '<img src="/images/sheldon.jpg" alt="Sheldon" class="rounded-box pic-frame" />'            
        elif 'leonard' in character.lower():
            return '<img src="/images/leonard.jpg" alt="Leonard" class="rounded-box pic-frame" />'
        elif 'penny' in character.lower():
            return '<img src="/images/penny.jpg" alt="Penny" class="rounded-box pic-frame" />'
        elif 'howard' in character.lower():
            return '<img src="/images/howard.jpg" alt="Howard" class="rounded-box pic-frame" />'
        elif 'raj' in character.lower():
            return '<img src="/images/raj.jpg" alt="Raj" class="rounded-box pic-frame" />'
        elif 'bernadette' in character.lower():
            return '<img src="/images/bernadette.jpg" alt="Bernadette" class="rounded-box pic-frame" />'
        elif 'amy' in character.lower():
            return '<img src="/images/amy.jpg" alt="Amy" class="rounded-box pic-frame" />'
        elif 'priya' in character.lower():
            return '<img src="/images/priya.jpg" alt="Priya" class="rounded-box pic-frame" />'
        elif 'stuart' in character.lower():
            return '<img src="/images/stuart.jpg" alt="Stuart" class="rounded-box pic-frame" />'
        elif 'leslie' in character.lower():
            return '<img src="/images/leslie.jpg" alt="Leslie" class="rounded-box pic-frame" />'
        elif 'zack' in character.lower():
            return '<img src="/images/zack.jpg" alt="Zack" class="rounded-box pic-frame" />'
        else:
            return character

    def get(self):
        season = self.request.get('season').strip()
        if not season or not season.isnumeric():
            self.my_renderer(errormsg='Invalid season: ' + season)
            return
        else:
            season = int(season)
        
        episode = self.request.get('episode')
        if not episode or not episode.isnumeric():
            self.my_renderer(errormsg='Invalid episode: ' + episode)
            return
        else:
            episode = int(episode)

        # get transcript from memcache/datastore
        memcache_index = str(season * 100 + episode) # key
        cached_transcript = memcache.get(memcache_index)
        if cached_transcript:
            title = cached_transcript[0]
            transcript = cached_transcript[1]
        else:
            show = BigBangTheory.get_by_key_name(memcache_index)
            if show:
                title = show.title
                transcript = show.transcript
            else:
                self.my_renderer(errormsg='Show does not exist: ' + memcache_index)
                return
        
        # divide transcript into components
        processed_transcript = []
        for line in transcript.split('\n'):
            i = line.find('%%')
            j = line.find(':')
            lineno = line[:i-1]
            character = line[i+3:j]
            if len(character) < 2 or 'credits' in character.lower():
                continue
            character = self.get_img_tag(character)
            dialogue = line[j+1:]
            processed_transcript.append([lineno, character, dialogue])

        # 'aal iz well' , render the page :)
        self.my_renderer(season=season, episode=episode, title=title, transcript=processed_transcript)


class KnockHandler(webapp2.RequestHandler):
    """ Shhhh! Secret """
    def get(self):
        self.response.out.write(self.request)


class UnexpectedErrorHandler(webapp2.RequestHandler):
    """ unused """
    def get(self):
        msg = self.request.get('message')
        self.response.out.write('Error message: '+ msg)

"""
class Custom404(webapp2.RequestHandler):
    def get(self, path):
        self.response.status_int = 404
        template = jinja_environment.get_template('/404/index.htm')
        self.response.out.write(template.render())
"""

mappings = webapp2.WSGIApplication([('/', HomeHandler),
                                ('/search', SearchHandler),
                                ('/view', ViewHandler),
                                ('/knockknock', KnockHandler),
                                ('/error', UnexpectedErrorHandler)],
                                #('/(.+)', Custom404)], 
                                debug = DEBUG)

