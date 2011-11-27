# twitterstream-to-mongodb

## DESCRIPTION

Simple python script for storing tweets from the twitter stream directly to a [MongDB](http://www.mongodb.org/) database based on a list of terms.

## FEATURES/PROBLEMS

The script runs forever and refreshes the terms list periodically. Terms list can be modified while the scripts runs. 

A catalog is created for each term in the MongoDB database.

Improvements apreciated.

## USAGE

	python twitterstreamtomongodb.py --user=gdelfresno --password=XXXXXXX --server=localhost --database=TwitterStream --file=terms-example.txt

The file just contains the search terms, each one in a line.

user and password are from a Twitter account

## REQUIREMENTS

###mongo-python-driver
[https://github.com/mongodb/mongo-python-driver](https://github.com/mongodb/mongo-python-driver)

###tweetstream
[https://bitbucket.org/runeh/tweetstream/src](https://bitbucket.org/runeh/tweetstream/src)

## LICENSE:

Twitter Stream To MongoDB (c) by gdelfresno

Twitter Stream To MongoDB is licensed under a
Creative Commons Attribution-NonCommercial 3.0 Unported License.

You should have received a copy of the license along with this
work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.