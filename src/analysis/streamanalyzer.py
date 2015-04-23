'''
Created on 04/10/2012

@author: gdelfresno
'''
from pymongo import MongoClient
from bson.code import Code
from bson import json_util
from bson.objectid import ObjectId
from optparse import OptionParser
from datetime import datetime

import simplejson as json


def get_parser():
    optParser = OptionParser()
    optParser.add_option("-d", "--database", dest="database", help="mongodb database name")
    optParser.add_option("-s", "--server", dest="server", help="mongodb host")
    optParser.add_option("-t", "--term", dest="term", help="collection name")
    optParser.add_option("-m", "--mapcollection", dest="mapcollection", help="map reduce collection")
    optParser.add_option("-o", "--output", dest="output", help="output file")
    optParser.add_option("-i", "--start", dest="start", help="start date", default=None)
    optParser.add_option("-e", "--end", dest="end", help="end date", default=None)
    optParser.add_option("-k", "--mode", dest="mode", default="users",
                      help="interaction mode: users or tweets [default: %default]")
    optParser.usage = "bad parametres"
    return optParser


optParser = get_parser()
(options, args) = optParser.parse_args()

host = options.server
database = options.database
term = options.term
mapcollection = options.mapcollection
output = options.output
start = None if options.start is None else datetime.strptime(options.start,"%d/%m/%Y")
end = None if options.end is None else datetime.strptime(options.end,"%d/%m/%Y")
mode = options.mode

def getDateQuery(start_date,end_date): 

    oid_start = ObjectId.from_datetime(start_date)
    oid_stop = ObjectId.from_datetime(end_date)
    
    return { "_id" : { "$gte" : oid_start, "$lt" : oid_stop } }

try:
    mongo = MongoClient(host)
except:
    print "Error starting MongoDB"
    raise

db = mongo[database]
collection = db[term]

def analyzeTweets():
    if not mapcollection in db.collection_names():
        mapF = Code(open('mapReduce/mapFunctionTweets.js','r').read())
        reduceF = Code(open('mapReduce/reduceFunctionTweets.js','r').read())
        collection.map_reduce(mapF,reduceF,out=mapcollection)

    jsonFile = open(output,'wb')
    jsonFile.write('[')
    first = True
        
    for doc in db[mapcollection].find().sort([('value', -1)]).limit(50):
        if first:
            first=False
        else:
            jsonFile.write(',')
        jsonFile.write(json.dumps(doc, indent=2, default=json_util.default))
        
    jsonFile.write(']')
    jsonFile.close()
    
    
def analyzeUsers():
    if not mapcollection in db.collection_names():
        mapF = Code(open('mapReduce/mapFunctionUsers.js','r').read())
        reduceF = Code(open('mapReduce/reduceFunctionUsers.js','r').read())
        query = getDateQuery(start,end)
        print query
        collection.map_reduce(mapF,reduceF,mapcollection,query=query)

    jsonFile = open(output,'wb')
    jsonFile.write('[')
    first = True
    
        
    for doc in db[mapcollection].find().sort([('value.rt', -1)]).limit(500):
        if first:
            first=False
        else:
            jsonFile.write(',')
        jsonFile.write(json.dumps(doc, indent=2, default=json_util.default))
        
    jsonFile.write(']')
    jsonFile.close()

if mode == 'users':
    analyzeUsers()
elif mode == 'tweets':
    analyzeTweets()
else:
    print "Unknow mode. It should be users or tweets"
