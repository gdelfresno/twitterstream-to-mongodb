"""
Created on 07/10/2012

@author: gdelfresno
"""
from optparse import OptionParser
from datetime import datetime

from pymongo import MongoClient
from bson.code import Code
from bson.objectid import ObjectId
from gexf import Gexf


def get_parser():
    opt_parser = OptionParser()
    opt_parser.add_option("-d", "--database", dest="database", help="mongodb database name")
    opt_parser.add_option("-s", "--server", dest="server", help="mongodb host", default=None)
    opt_parser.add_option("-t", "--term", dest="term", help="collection name")
    opt_parser.add_option("-m", "--mapcollection", dest="mapcollection", help="map reduce collection")
    opt_parser.add_option("-o", "--output", dest="output", help="output file")
    opt_parser.add_option("-i", "--start", dest="start", help="start date", default=None)
    opt_parser.add_option("-e", "--end", dest="end", help="end date", default=None)
    opt_parser.usage = "bad parametres"
    return opt_parser


optParser = get_parser()
(options, args) = optParser.parse_args()

host = options.server
database = options.database
term = options.term
mapcollection = options.mapcollection
output = options.output

start = None if options.start is None else datetime.strptime(options.start, "%d/%m/%Y")
end = None if options.end is None else datetime.strptime(options.end, "%d/%m/%Y")


def get_date_query(start_date, end_date):
    if start_date is not None and end_date is not None:
        oid_start = ObjectId.from_datetime(start_date)
        oid_stop = ObjectId.from_datetime(end_date)

        return {"_id": {"$gte": oid_start, "$lt": oid_stop}}
    else:

        return None


try:
    mongo = MongoClient(host)
except:
    print "Error starting MongoDB"
    raise

db = mongo[database]
collection = db[term]
# db.drop_collection(mapcollection)
if mapcollection not in db.collection_names():
    mapF = Code(open('../mapReduce/mapGraph.js', 'r').read())
    reduceF = Code(open('../mapReduce/reduceGraph.js', 'r').read())
    collection.map_reduce(mapF, reduceF, query=get_date_query(start, end), out=mapcollection)

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
    node.addAttribute(giid, str(user['value']['indegree']))
    node.addAttribute(goid, str(user['value']['outdegree']))
    node.addAttribute(gort, str(user['value']['rts']))
    node.addAttribute(gomt, str(user['value']['mts']))
    userNodeMap[user['_id']] = node

for name in userMap.keys():
    outlinks = userMap[name]['outlinks']
    for link in outlinks:
        if link != name and link in userMap.keys():
            graph.addEdge(name + ":" + link, userNodeMap[name].id, userNodeMap[link].id)

output_file = open(output, 'w')
gexf.write(output_file)
