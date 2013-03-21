'''
Created on 07/10/2012

@author: gdelfresno
'''
from pymongo import Connection
from bson.code import Code
from bson import json_util
from bson.objectid import ObjectId
from optparse import OptionParser
from dateutil import parser
from gexf import Gexf

import datetime
from datetime import datetime

import simplejson as json


def get_parser():
    optParser = OptionParser()
    optParser.add_option("-d", "--database", dest="database", help="mongodb database name")
    optParser.add_option("-s", "--server", dest="server", help="mongodb host", default=None)
    optParser.add_option("-t", "--term", dest="term", help="collection name")
    optParser.add_option("-m", "--mapcollection", dest="mapcollection", help="map reduce collection")
    optParser.add_option("-o", "--output", dest="output", help="output file")
    optParser.add_option("-i", "--start", dest="start", help="start date", default=None)
    optParser.add_option("-e", "--end", dest="end", help="end date", default=None)
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

def getDateQuery(start_date,end_date): 

    if not start_date is None and not end_date is None:
        oid_start = ObjectId.from_datetime(start_date)
        oid_stop = ObjectId.from_datetime(end_date)
        
        return { "_id": { "$gte": oid_start, "$lt": oid_stop } }
    else:

        return None

try:
    mongo = Connection(host)
except:
    print "Error starting MongoDB"
    raise

db = mongo[database]
collection = db[term]
# db.drop_collection(mapcollection)
if not mapcollection in db.collection_names():
    mapF = Code(open('../mapReduce/mapGraph.js','r').read())
    reduceF = Code(open('../mapReduce/reduceGraph.js','r').read())
    collection.map_reduce(mapF,reduceF,query=getDateQuery(start,end), out=mapcollection)

gexf = Gexf(creator="lomo", description="Relations")
graph = gexf.addGraph(type="directed", mode="static", label="relations")
giid = graph.addNodeAttribute("Global Indegree", "0", type="float")
goid = graph.addNodeAttribute("Global Outdegree", "0", type="float")
gort = graph.addNodeAttribute("Retweets", "0", type="float")
gomt = graph.addNodeAttribute("Mentions", "0", type="float")
userMap = {} 
userNodeMap = {}
for user in db[mapcollection].find().sort([('value.indegree', -1)]):
    userMap[user['_id']] = user['value']
    node = graph.addNode(user['_id'], user['_id'])
    node.addAttribute(giid, user['value']['indegree'])
    node.addAttribute(goid, user['value']['outdegree'])
    node.addAttribute(gort, user['value']['rts'])
    node.addAttribute(gomt, user['value']['mts'])
    userNodeMap[user['_id']] = node
    
for name in userMap.keys():
    outlinks = userMap[name]['outlinks']
    for link in outlinks:
        if link != name and link in userMap.keys():
            graph.addEdge(name + ":" + link, userNodeMap[name].id, userNodeMap[link].id)

file = open(output, 'w')
gexf.write(file)
