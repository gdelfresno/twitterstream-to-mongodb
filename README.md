# twitterstream-to-mongodb

## DESCRIPTION

Simple python script for storing tweets from the twitter stream directly to a [MongoDB](http://www.mongodb.org/) database based on a list of terms.

## FEATURES/PROBLEMS

The script runs forever and refreshes the terms list periodically. Terms list can be modified while the scripts runs. 

A catalog is created for each term in the MongoDB database.

Improvements apreciated.

## CLONE AND USE

    git clone git://github.com/gdelfresno/twitterstream-to-mongodb.git
    cd twitterstream-to-mongodb/src
    python twitterstreamtomongodb.py --oauth=oauth-example.json --server=localhost --port=23717 --database=TwitterStream --dbauth=dbauth.json --track=terms-example.txt --retweets=False
	
### USAGE EXPLAINED
    :arg oauth: json file that outlines oauth credentials for Twitter developers
    :arg server: default is localhost for basic/local mongodb instances
    :arg port: optional port of the mongodb instance
    :arg database: the name you would like the database to have
    :arg dbauth: auth file with database credentials
    :arg track: basic text outlining search terms such as #trending or @user_name (carriage return per entry)
    :arg retweets: specify whether or not retweets are collected and stored in the database

#### DATABASE AUTH (json)

    {
        "user" : "yor_user",
        "password" : "your_password"
    }

#### OAUTH (json)

_Oauth Authentication_:

    {
        "consumer_key" : "ThIsIsJuStAnExAmPlE",
        "consumer_secret" : "ThIsIsJuStAnExAmPlE",
        "access_token" : "ThIsIsJuStAnExAmPlE",
        "access_token_secret" : "ThIsIsJuStAnExAmPlE"
    }

_Basic Authentication_:

    {
        "username" : "twitter_username"
        "password" : "password"
    }

#### TRACK (basic text)
    
    SomeWord
    @user_name
    #hashtag

## REQUIREMENTS

### Install from requirements file

    pip install -r requirements.txt

### mongo-python-driver
[https://github.com/mongodb/mongo-python-driver](https://github.com/mongodb/mongo-python-driver)

    pip install pymongo
    
#### If this doesn't work, install from source

    git clone git://github.com/mongodb/mongo-python-driver.git pymongo
    cd pymongo/
    python setup.py install

### tweepy
[https://github.com/tweepy/tweepy](https://github.com/tweepy/tweepy)

    pip install tweepy

## LICENSE:

    Twitter Stream To MongoDB (c) by gdelfresno

    Twitter Stream To MongoDB is licensed under 
    the terms of the GNU General Public License 
    as published by the Free Software Foundation.
