"""
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
"""

import threading
import datetime
import time
import re

from optparse import OptionParser
from pymongo import MongoClient

from ssl import SSLError

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream, API
from tweepy.utils import import_simplejson

json = import_simplejson()

active_terms = {}


def get_parser():
    the_parser = OptionParser()
    the_parser.add_option("-d", "--database", dest="database", help="mongodb database name")
    the_parser.add_option("-s", "--server", dest="server", help="mongodb host")
    the_parser.add_option("-p", "--port", dest="port", help="mongodb port", type="int")
    the_parser.add_option("-a", "--dbauth", dest="dbauth", help="db auth file")
    the_parser.add_option("-o", "--oauth", dest="oauthfile", help="file with oauth options")
    the_parser.add_option("-t", "--track", dest="track", help="track terms file")
    the_parser.add_option("-f", "--follow", dest="follow", help="follow users file")
    the_parser.add_option("-e", "--exclude-retweets", action="store_true", dest="exclude_retweets",
                          help="Exclude retweets from stream", default=False)
    the_parser.usage = "bad parametres"
    return the_parser


def update_search_query(the_options, stream_thread):
    print 'Updating terms: %s' % datetime.datetime.now()

    query = ",".join(active_terms.keys())

    stream_thread.stop_consume()

    follow = False
    if the_options.follow and not the_options.track:
        follow = True

    stream_thread = StreamConsumerThreadClass(query, the_options.oauthfile, follow)
    stream_thread.setDaemon(True)

    stream_thread.start()


def add_term(term):
    if term == '':
        return

    active_terms[term] = term


def delete_term(term):
    if term == '':
        return

    active_terms.pop(term)


def update_terms(options, stream_thread, items_file):
    fileterms = []

    update = False
    f = file(items_file, 'r')
    for line in f.readlines():
        term = str.strip(line)

        fileterms.append(term)
        # Check new terms
        if term not in active_terms.keys():
            print "New Term: %s" % term
            add_term(term)
            update = True

    for current in active_terms.keys():
        if current not in fileterms:
            print "Deleted term: %s" % current
            delete_term(current)
            update = True

    if update:
        update_search_query(options, stream_thread)


def pretty_print_status(status):
    text = status["text"]
    description = status['user']['screen_name']
    if "retweeted_status" in status:
        description = "%s RT by %s" % (
            status["retweeted_status"]["user"]["screen_name"], status['user']['screen_name'])
        text = status["retweeted_status"]["text"]

    try:
        return '[%s][%-36s]: %s' % (status['created_at'], description, text)
    except UnicodeEncodeError:
        return "Can't decode UNICODE tweet"
    # except:
    #     return "Error printing status"


class MongoDBCoordinator:
    def __init__(self, host='localhost', port=None, database='TwitterStream', authfile=None):
        try:
            if port is not None:
                self.mongo = MongoClient(host, int(port))
            else:
                self.mongo = MongoClient(host)
        except:
            print "Error starting MongoDB"
            raise

        self.db = self.mongo[database]

        if authfile is not None:

            try:
                dbauth = json.loads(open(authfile, 'r').read())
                if not self.db.authenticate(dbauth["user"], dbauth["password"]):
                    raise Exception("Invalid database credentials")

            except:
                print "Error authenticating database"
                raise

        self.tuits = {}

    def add_tuit(self, tweet):
        for term in active_terms.keys():

            if "retweeted_status" in tweet:
                content = tweet["retweeted_status"]["text"]
            else:
                content = tweet['text']

            strre = re.compile(term, re.IGNORECASE)
            match = strre.search(content)

            if match:
                if term not in self.db.collection_names():
                    self.db.create_collection(term)

                collection = self.db[term]
                collection.save(tweet)

                try:
                    print "[%-15s]%s" % (term, pretty_print_status(tweet))
                except Exception, e:
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
            if program_options.exclude_retweets:
                pass
            else:
                jstatus = json.loads(data)
                mongo.add_tuit(jstatus)

        elif 'in_reply_to_status_id' in data:
            jstatus = json.loads(data)
            mongo.add_tuit(jstatus)

        elif 'delete' in data:
            delete = json.loads(data)['delete']['status']
            if self.on_delete(delete['id'], delete['user_id']) is False:
                return False

        elif 'limit' in data:
            if self.on_limit(json.loads(data)['limit']['track']) is False:
                return False

    def on_error(self, status_code):
        if status_code == 401:
            raise Exception("Invalid loging credentials")
        else:
            print "Error received %d" % status_code

    def on_limit(self, track):
        print "###### LIMIT ERROR #######"


# Class that track the stream
class StreamConsumerThreadClass(threading.Thread):
    def __init__(self, term='', oauthfile='', follow=False):
        threading.Thread.__init__(self)
        self.searchterm = term
        self.name = term
        self.consume = True
        self.follow = follow
        listener = MongoDBListener()

        try:
            oauth = json.loads(open(oauthfile, 'r').read())

            if 'consumer_key' in oauth:
                auth = OAuthHandler(oauth['consumer_key'], oauth['consumer_secret'])
                auth.set_access_token(oauth['access_token'], oauth['access_token_secret'])
                self.api = API(auth)

                if not self.api.verify_credentials():
                    raise Exception("Invalid credentials")

                self.stream = Stream(auth, listener, timeout=60)

        except:
            print "Error logging to Twitter"
            raise

    def stop_consume(self):
        self.stream.disconnect()

    def run(self):
        now = datetime.datetime.now()
        print "Twitter Stream with terms: %s started at: %s" % (self.getName(), now)

        connected = False
        while True:
            try:
                if not connected:
                    connected = True
                    if self.follow:
                        user_ids = []
                        for user in self.api.lookup_users([], self.searchterm.split(','), False):
                            user_ids.append(user.id)

                        self.stream.filter(follow=[",".join("{0}".format(n) for n in user_ids)])
                    else:
                        self.stream.filter(track=[self.searchterm])

            except SSLError, sse:
                print sse
                connected = False
            except Exception, e:
                print "Stream error"
                raise e


if __name__ == "__main__":
    parser = get_parser()
    (program_options, args) = parser.parse_args()
    print program_options, args

    if program_options.follow and program_options.track:
        print "--track and --follow options are incompatible yet, --track will be used"

    if program_options.follow is None and program_options.track is None:
        print "You must pass one of this options --track and --follow"
        print "Exiting"
        exit(0)

    terms_file = program_options.follow
    if program_options.track:
        terms_file = program_options.track

    try:
        mongo = MongoDBCoordinator(program_options.server, program_options.port, program_options.database,
                                   program_options.dbauth)
        stream = StreamConsumerThreadClass('', program_options.oauthfile)
        try:
            while True:
                update_terms(program_options, stream, terms_file)
                time.sleep(5)

        except KeyboardInterrupt, ke:
            print "Closing stream"
            stream.stop_consume()
    except Exception, t:
        print t
        exit(0)

