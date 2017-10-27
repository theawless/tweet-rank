import random

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pymongo import MongoClient


client = MongoClient()
db = client['vegas']


def tweet_length(tweet):
	return len(tweet['text'])


def tweet_is_retweet(tweet):
	if 'retweeted_status' in tweet:
		return True

	return False


def tweet_is_reply(tweet):
	pass


def reply_count(tweet):
	pass


def word_count(tweet):
	pass


def extract_features(tweet):
	return {
		'id': tweet['id_str'],
		'score': tweet['score'],
		'tweet_len': tweet_length(tweet),
		'tweet_is_reply': tweet_is_retweet(tweet)
	}


# Returns dataframe from list of tweets
def compute_dataframe(tweets):
	return pd.DataFrame([extract_features(tweet) for tweet in tweets])


def main():
	tweets = []
	for tweet in db.tweets.find():
		# Not required if using annotated tweets
		tweet['score'] = random.randint(1,5)
		tweets.append(tweet)
	
	dataframe = compute_dataframe(tweets)	
	dataframe.to_csv('tweets_ann.csv', sep='\t')





if __name__ == '__main__':
	main()

