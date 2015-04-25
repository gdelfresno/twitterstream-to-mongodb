"""
Created on 04/10/2012

@author: gdelfresno
"""
from pymongo import MongoClient
from bson.code import Code
from bson import json_util
from bson.objectid import ObjectId
from optparse import OptionParser
from datetime import datetime

import simplejson as json


def get_parser():
    the_parser = OptionParser()
    the_parser.add_option("-d", "--database", dest="database", help="mongodb database name")
    the_parser.add_option("-s", "--server", dest="server", help="mongodb host")
    the_parser.add_option("-t", "--term", dest="term", help="collection name")
    the_parser.add_option("-m", "--mapcollection", dest="mapcollection", help="map reduce collection")
    the_parser.add_option("-o", "--output", dest="output", help="output file")
    the_parser.add_option("-i", "--start", dest="start", help="start date", default=None)
    the_parser.add_option("-e", "--end", dest="end", help="end date", default=None)
    the_parser.add_option("-k", "--mode", dest="mode", default="users",
                          help="interaction mode: users or tweets [default: %default]")
    the_parser.usage = "bad parametres"
    return the_parser


opt_parser = get_parser()
(options, args) = opt_parser.parse_args()

host = options.server
database = options.database
term = options.term
mapcollection = options.mapcollection
output = options.output
start = None if options.start is None else datetime.strptime(options.start, "%d/%m/%Y")
end = None if options.end is None else datetime.strptime(options.end, "%d/%m/%Y")
mode = options.mode


def get_date_query(start_date, end_date):
    oid_start = ObjectId.from_datetime(start_date)
    oid_stop = ObjectId.from_datetime(end_date)

    return {"_id": {"$gte": oid_start, "$lt": oid_stop}}


try:
    mongo = MongoClient(host)
except:
    print "Error starting MongoDB"
    raise

db = mongo[database]
collection = db[term]


def analyze_tweets():
    if mapcollection not in db.collection_names():
        map_function = Code(open('mapReduce/mapFunctionTweets.js', 'r').read())
        reduce_function = Code(open('mapReduce/reduceFunctionTweets.js', 'r').read())
        collection.map_reduce(map_function, reduce_function, out=mapcollection)

    json_file = open(output, 'wb')
    json_file.write('[')
    first = True

    for doc in db[mapcollection].find().sort([('value', -1)]).limit(50):
        if first:
            first = False
        else:
            json_file.write(',')
        json_file.write(json.dumps(doc, indent=2, default=json_util.default))

    json_file.write(']')
    json_file.close()


def analyze_users():
    if mapcollection not in db.collection_names():
        map_function = Code(open('mapReduce/mapFunctionUsers.js', 'r').read())
        reduce_function = Code(open('mapReduce/reduceFunctionUsers.js', 'r').read())
        query = get_date_query(start, end)
        print query
        collection.map_reduce(map_function, reduce_function, mapcollection, query=query)

    json_file = open(output, 'wb')
    json_file.write('[')
    first = True

    for doc in db[mapcollection].find().sort([('value.rt', -1)]).limit(500):
        if first:
            first = False
        else:
            json_file.write(',')
        json_file.write(json.dumps(doc, indent=2, default=json_util.default))

    json_file.write(']')
    json_file.close()


if mode == 'users':
    analyze_users()
elif mode == 'tweets':
    analyze_tweets()
else:
    print "Unknow mode. It should be users or tweets"
