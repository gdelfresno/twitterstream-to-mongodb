'''
Twitter Stream To MongoDB (c) by gdelfresno

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import threading
import datetime
import time
import re

from optparse import OptionParser
from pymongo import Connection

from ssl import SSLError

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream, API
from tweepy.utils import import_simplejson

json = import_simplejson()

active_terms = {}

STREAM_URL = "https://stream.twitter.com/1/statuses/filter.json?track=%s"


def get_parser():
    parser = OptionParser()
    parser.add_option("-d", "--database", dest="database", help="mongodb database name")
    parser.add_option("-s", "--server", dest="server", help="mongodb host")
    parser.add_option("-p", "--port", dest="port", help="mongodb port", type="int")
    parser.add_option("-a", "--dbauth", dest="dbauth", help="db auth file")
    parser.add_option("-o", "--oauth", dest="oauthfile", help="file with oauth options")
    parser.add_option("-t", "--track", dest="track", help="track terms file")
    #parser.add_option("-a", "--all_keys", dest="all_keys", help="MongoDB receives all keys from json (True/False)")
    #parser.add_option("-u", "--use_keys", dest="use_keys", help="MongoDB receieves subset of keys from json (list)")
    parser.add_option("-r", "--retweets", dest="retweets", help="Allow retweets into MongoDB")
    parser.usage = "bad parametres"
    return parser


def updateSearchQuery(options):
    print 'Updating terms: %s' % datetime.datetime.now()

    query = ",".join(active_terms.keys())

    try:
        streamThread.stopConsume()

    except:
        pass

    streamThread = StreamConsumerThreadClass(query, options.oauthfile)
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
    f = file(options.track, 'r')
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
    except UnicodeEncodeError:
        return "Can't decode UNICODE tweet"
    except :
        return "Error printing status"


class MongoDBCoordinator:
    def __init__(self, host='localhost', port=None, database='TwitterStream', authfile=None):
        try:
            if not port is None:
                self.mongo = Connection(host, int(port))
            else:
                self.mongo = Connection(host)
        except:
            print "Error starting MongoDB"
            raise
        
        self.db = self.mongo[database]

        if not authfile is None:
            
            try:
                dbauth = json.loads(open(authfile, 'r').read())
                if not self.db.authenticate(dbauth["user"], dbauth["password"]):
                    raise Exception("Invalid database credentials")

            except:
                print "Error authenticating database"
                raise
        
        self.tuits = {}


    def addTuit(self, tweet):
        for term in active_terms.keys():
            
            if "retweeted_status" in tweet:
                content = tweet["retweeted_status"]["text"]
            else:
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


class MongoDBListener(StreamListener):
    """
    A listener handles tweets are the received from the stream. 
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
        """
        Called when raw data is received from connection.

        Override this method if you wish to manually handle
        the stream data. Return False to stop stream and close connection.
        """
        if 'retweeted_status' in data:
            if options.retweets in ["False", "F", "false", "f"]:
                pass
            else:
                jstatus = json.loads(data)
                mongo.addTuit(jstatus)

        elif 'in_reply_to_status_id' in data:
            jstatus = json.loads(data)
            mongo.addTuit(jstatus)

        elif 'delete' in data:
            delete = json.loads(data)['delete']['status']
            if self.on_delete(delete['id'], delete['user_id']) is False:
                return False

        elif 'limit' in data:
            if self.on_limit(json.loads(data)['limit']['track']) is False:
                return False

    def on_error(self, status_code):
        print "Error received %d" % status_code
        return

    def on_limit(self, track):
        print "###### LIMIT ERROR #######"


#Class that track the stream
class StreamConsumerThreadClass(threading.Thread):
    def __init__(self, term='', oauthfile=''):
        threading.Thread.__init__(self)
        self.searchterm = term
        self.name = term
        self.consume = True
        
        listener = MongoDBListener()
        
        try:
            oauth = json.loads(open(oauthfile, 'r').read())
            
            auth = OAuthHandler(oauth['consumer_key'], oauth['consumer_secret'])
            auth.set_access_token(oauth['access_token'], oauth['access_token_secret'])

            api = API(auth)

            if not api.verify_credentials():
                raise Exception("Invalid credentials")

        except:
            print "Error logging to Twitter"
            raise
    
        self.stream = Stream(auth, listener, timeout=60)  


    def stopConsume(self):
        self.stream.disconnect()


    def run(self):
        now = datetime.datetime.now()
        print "Twitter Stream with terms: %s started at: %s" % (self.getName(), now)
        
        connected = False
        while True:
            try: 
                if not connected:
                    connected = True
                    self.stream.filter(track=[self.searchterm])
            
            except SSLError, e:
                print e
                connected = False            


if __name__ == "__main__":
    parser = get_parser()
    (options, args) = parser.parse_args()
    print options, args
    
    try:
        mongo = MongoDBCoordinator(options.server, options.port, options.database, options.dbauth)
        streamThread = StreamConsumerThreadClass('', options.oauthfile)
    except Exception, e:
        print e
        exit(0)

    try:
        while True:
            updateTerms(options)
            time.sleep(5)

    except KeyboardInterrupt, e:
        print "Closing stream"
        streamThread.stopConsume()
