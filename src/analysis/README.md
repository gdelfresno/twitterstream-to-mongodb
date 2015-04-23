# graphextractor.py

Generates a relation graph for one term in the mongo database.

* Nodes: Users
* Edges: Interactions (RTs, Replies, Mentions)

The graph is in [gexf](http://gexf.net/format) format and can be imported directly to [Gephi](https://gephi.github.io/)

# streamanalyzer.py

Generates JSON files with stats about terms

* Users: Number of tweets, RTs, mentions and replies, last three both done and received
* Tweets: Just each tweet with the numbers of RTs

## Usage

Both scripts use the same main arguments    
    
    :arg server: mongodb host
    :arg database: database of terms
    :arg term: term (collecion) used to make graph
    :arg mapcollection: temporary collection to store the map-reduce results
    :arg output: genearated gefx file path
    :arg start: Start date
    :arg end: End date
    
streamanalyzer.py also requires a mode

    :arg mode: users or tweets

## Example

    graphextractor.py -d Stream -s localhost -t Netflix -m mapreduce -o Netflix_graph.gexf
    
    streamanalyzer.py -d Stream -s localhost -t Netflix -m mapreduce -o Netflix_graph.gexf