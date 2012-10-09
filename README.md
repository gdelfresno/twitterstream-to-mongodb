# twitterstream-to-mongodb

## DESCRIPTION

Simple python script for storing tweets from the twitter stream directly to a [MongDB](http://www.mongodb.org/) database based on a list of terms.

## FEATURES/PROBLEMS

The script runs forever and refreshes the terms list periodically. Terms list can be modified while the scripts runs. 

A catalog is created for each term in the MongoDB database.

Improvements apreciated.

## USAGE

	python twitterstreamtomongodb.py --user=oauth-file.json --server=localhost --database=TwitterStream --file=terms-example.txt

The file just contains the search terms, each one in a line.

You need to configure an app and the oauth tokens an put it in a file in this way

	{
		"consumer_key" : "uEQ04CG23CIl4SsRhDKM3w",
		"consumer_secret" : "06Te8HQVG0A5Ce3ToAdiAhmWVpNavY1RIIn76wjUZJ8",
		"access_token" : "yJCy4-sj0oZ3QUDBtcu6KisGVp7QhJlNbb3966tDceFW585638j8pyg",
		"access_token_secret" : "xgt1KMnzAkpulPpAVGLND7IOxuCVSmClK7oBvI"
	}

## REQUIREMENTS

###mongo-python-driver
[https://github.com/mongodb/mongo-python-driver](https://github.com/mongodb/mongo-python-driver)

###tweepy
[https://github.com/tweepy/tweepy](https://github.com/tweepy/tweepy)

## LICENSE:

Twitter Stream To MongoDB (c) by gdelfresno

Twitter Stream To MongoDB is licensed under the terms of the GNU General Public License as published by the Free Software Foundation.