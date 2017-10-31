import random
import string
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pymongo import MongoClient


client = MongoClient()
db = client['vegas']

EVENT_TIME = 0

def tweet_length(tweet):
	return len(tweet['text'])


def word_count(tweet):
	return len(re.findall(r'\w+', tweet['text']))


def contains_question_mark(tweet):
	return '?' in tweet['text']


def contains_exclamation_mark(tweet):
	return '!' in tweet['text']


def contains_multiple_ques_excl_mark(tweet):
	return tweet['text'].count('?') > 1 or tweet['text'].count('!') > 1


def contains_second_pronoun(tweet):
	second_pronouns = ['you','yours','yourself']
	for word in tweet['text'].strip().split():
		for pronoun in second_pronouns:
			if word == pronoun:
				return True

	return False


def contains_third_pronoun(tweet):
	third_pronouns = ['she','her','him','it','he','they','them']
	for word in tweet['text'].strip().split():
		for pronoun in second_pronouns:
			if word == pronoun:
				return True

	return False


def fraction_of_uppercase(tweet):
	text = re.sub(r"http\S+", "", tweet['text'])
	t_count = len(text)
	u_count = sum(1 for c in text if c.isupper())
	return float(u_count)/t_count


def url_count(tweet):
	return len(re.findall(r'http\S+',tweet['text']))


def contains_user_mention(tweet):
	return len(tweet['entities']['user_mentions']) > 0


def contains_hashtag(tweet):
	return len(tweet['entities']['hashtags']) > 0


def is_retweet(tweet):
	return 'retweeted_status' in tweet


def is_reply(tweet):
	return tweet['in_reply_status_id'] != None


def retweet_count(tweet):
	return tweet['retweet_count']


def reply_count(tweet):
	return tweet['reply_count']


def num_positive_words(tweet):
	pass


def num_negative_words(tweet):
	pass


def tweeted_before_event(tweet):
	return tweet['created_at'] < EVENT_TIME


def is_quoted_status(tweet):
	return 'quoted_status_id' in tweet


# If near tweet posted near event location
# None if coordinates not in tweet
def vicinity_of_event(tweet):
	pass


def days_since_join(tweet):
	return EVENT_TIME - tweet['user']['created_at']


def status_count(tweet):
	return tweet['user']['status_count']


def is_verified(tweet):
	return tweet['user']['verified']


def non_empty_bio(tweet):
	return len(tweet['user']['description']) > 0


def follower_count(tweet):
	return tweet['user']['followers_count']


def friend_count(tweet):
	return tweet['user']['friends_count']


def extract_features(tweet):
	return {
		'id': tweet['id_str'],
		'score': tweet['score'],
		'tweet_length': tweet_length(tweet),
		'is_reply': tweet_is_retweet(tweet)
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

