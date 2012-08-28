'''
Twitter Stream To MongoDB (c) by gdelfresno

Twitter Stream To MongoDB is licensed under a
Creative Commons Attribution-NonCommercial 3.0 Unported License.

You should have received a copy of the license along with this
work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.
'''

import threading
import datetime
import time
import re

import tweetstream

from optparse import OptionParser
from pymongo import Connection

active_terms = {}

STREAM_URL = "https://stream.twitter.com/1/statuses/filter.json?track=%s"

def get_parser():
    parser = OptionParser()
    parser.add_option("-d", "--database", dest="database", help="mongodb database name")
    parser.add_option("-s", "--server", dest="server", help="mongodb host")
    parser.add_option("-u", "--user", dest="user", help="twitter user to connect with")
    parser.add_option("-p", "--password", dest="password", help="twitter password")
    parser.add_option("-f", "--file", dest="file", help="terms file")
    parser.usage = "bad parametres"
    return parser

def updateSearchQuery(options):
    print 'Updating terms: %s' % datetime.datetime.now()
    
    query = ",".join(active_terms.keys())
    
    try:
        streamThread.stopConsume()
    except:
        pass
    
    streamThread = StreamConsumerThreadClass(query,user=options.user,password=options.password)
    streamThread.setDaemon(True)
    
    streamThread.start()
    

def addTerm(term):
    if term == '':
        return
    active_terms[term] = term
    
def deleteTerm(term):
    if term == '':
        return
    active_terms.pop(term)
        
    
def updateTerms(options):
    
    fileterms = []
    
    update = False
    f = file(options.file,'r')
    for line in f.readlines():
        term = str.strip(line) 
        
        fileterms.append(term)
        #Check new terms
        if not term in active_terms.keys():
            print "New Term: %s" % term
            addTerm(term)
            update = True
            
        
    
    for current in active_terms.keys():
        if not current in fileterms:
            print "Deleted term: %s" % current
            deleteTerm(current)
            update = True
     
    if update:
        updateSearchQuery(options)
           
def prettyPrintStatus(status):
    text = status["text"]
    description = status['user']['screen_name']
    if "retweeted_status" in status:
        description = ("%s RT by %s") % (status["retweeted_status"]["user"]["screen_name"], status['user']['screen_name'])
        text = status["retweeted_status"]["text"]
    
    
    try:
        return '[%s][%-36s]: %s' % (status['created_at'], description, text)
    except:
        return "Error printing status"

class MongoDBCoordinator:
    def __init__(self,host='localhost',database='TwitterStream'):
        try:
            self.mongo = Connection(host)
        except:
            print "Error starting MongoDB"
            raise
        
        self.db = self.mongo[database]
        self.tuits = {}
    def addTuit(self,tweet):
        for term in active_terms.keys():
            
            content = tweet['text']
            
            strre = re.compile(term, re.IGNORECASE)
            match = strre.search(content)
            if match:
                
                if not term in self.db.collection_names():
                    self.db.create_collection(term)
                
                collection = self.db[term]
                collection.save(tweet)
        
                try:
                    print "[%-15s]%s" % (term, prettyPrintStatus(tweet))           
                except Exception as (e):
                    print "Error %s" % e.message

#Class that track the stream
class StreamConsumerThreadClass(threading.Thread):
    def __init__(self,term='',user='',password=''):
        threading.Thread.__init__(self)
        self.searchterm = term
        self.name = term
        self.consume = True
        self.user = user
        self.password = password
        
    def stopConsume(self):
        self.consume = False
      
    def run(self):
        now = datetime.datetime.now()
        print "Twitter Stream with terms: %s started at: %s" % (self.getName(), now)
        
        try:
            searchurl = STREAM_URL % self.searchterm
            stream = tweetstream.FilterStream(self.user,self.password,url=searchurl)
            for tweet in stream:
                try:
                    
                    mongo.addTuit(tweet)
                    if not self.consume:
                        break
                except Exception as (e):
                    print "Error %s" % e.message
            
            stream.close()
        except Exception as (e):
            print "Error %s" % e.message
 


if __name__ == "__main__":
    parser = get_parser()
    (options, args) = parser.parse_args()
    print options, args
    
    mongo = MongoDBCoordinator(options.server,options.database)
    streamThread = StreamConsumerThreadClass('',options.user,options.password)
    
    while True:
        updateTerms(options)
        time.sleep(5)

