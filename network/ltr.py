import random
import string
import re
import time

import nltk
import nltk.sentiment
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from geopy.distance import great_circle
from pymongo import MongoClient
from tqdm import tqdm


client = MongoClient()
db = client['vegas']

EVENT_TIME = 1506837900 # 10:05 PM 1st October, 2017 (PDT) 
EVENT_COORDINATE = (36.11470649999999, 115.17284840000002)	
DIST_THRESHOLD = 20 # in km

sentimentAnalyser = nltk.sentiment.vader.SentimentIntensityAnalyzer()


def tokenize_text(tweet, ascii=True, ignore_rt_char=True, ignore_url=True, 
				ignore_mention=True, ignore_hashtag=True, letter_only=True, 
				remove_stopwords=True, min_tweet_len=3):
	
	global model
	sword = nltk.corpus.stopwords.words('english')

	if ascii:  # maybe remove lines with ANY non-ascii character
		for c in tweet:
			if not (0 < ord(c) < 127):
				return ''

	tokens = tweet.lower().split()  # to lower, split
	res = []

	for token in tokens:
		if remove_stopwords and token in sword:
			continue
		if ignore_rt_char and token == 'rt':
			continue
		if ignore_url and token.startswith('https:'):
			continue
		if ignore_mention and token.startswith('@'):
			continue
		if ignore_hashtag and token.startswith('#'):
			continue
		if letter_only:
			if not token.isalpha():
				continue
		elif token.isdigit():
			token = '<num>'

		res += token,

	return res


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
		for pronoun in third_pronouns:
			if word == pronoun:
				return True

	return False


def fraction_of_uppercase(tweet):
	text = re.sub(r"http\S+", "", tweet['text'])
	text = re.sub(r"RT", "", tweet['text'])
	t_count = len(text)
	u_count = sum(1 for c in text if c.isupper())
	return float(u_count)/t_count


def url_count(tweet):
	return len(re.findall(r'http\S+',tweet['text']))


def contains_user_mention(tweet):
	return len(tweet['entities']['user_mentions']) > 0


def contains_hashtag(tweet):
	if 'hashtags' in tweet['entities']:
		return len(tweet['entities']['hashtags']) > 0

	return False


def is_retweet(tweet):
	if 'retweeted_status' in tweet:
		return True

	return False


def is_reply(tweet):
	if 'in_reply_status_id' in tweet:
		return True

	return False


def retweet_count(tweet):
	if 'retweet_count' in tweet:
		return tweet['retweet_count']

	return 0


def reply_count(tweet):
	if 'reply_count' in tweet:
		return tweet['reply_count']

	return 0


def tweet_sentiment(tweet):
	labels = {'pos': 1,'neg': -1,'neu': 0}
	sentence = ' '.join(tokenize_text(tweet['text']))
	scores = sentimentAnalyser.polarity_scores(sentence)
	scores.pop('compound', None)
	sentiment = max(scores, key=scores.get)	
	return labels[sentiment]


def tweeted_before_event(tweet):
	struct_time = time.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
	tweet_time = int(time.mktime(struct_time))

	return tweet_time < EVENT_TIME


def is_quoted_status(tweet):
	return 'quoted_status_id' in tweet


# If tweet posted near event location
# None if coordinates not in tweet
def vicinity_of_event(tweet):
	if not tweet['coordinates']:
		return None

	tweet_coord = (tweet['coordinates'][0], tweet['coordinates'][1])
	return great_circle(tweet_coord, EVENT_COORDINATE).km < DIST_THRESHOLD


def days_since_join(tweet):
	struct_time = time.strptime(tweet['user']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
	join_time = int(time.mktime(struct_time))
	
	return (EVENT_TIME - join_time)//86400


def status_count(tweet):
	return tweet['user']['statuses_count']


def is_verified(tweet):
	return tweet['user']['verified']


def non_empty_bio(tweet):
	if tweet['user']['description']:
		return len(tweet['user']['description']) > 0
	
	return False

def follower_count(tweet):
	return tweet['user']['followers_count']


def friend_count(tweet):
	return tweet['user']['friends_count']


def extract_features(tweet):
	return {
		'id': tweet['id_str'],
		'score': tweet['score'],
		'tweet_length': tweet_length(tweet),
		'word_count': word_count(tweet),
		'contains_question_mark': contains_question_mark(tweet),
		'contains_exclamation_mark': contains_exclamation_mark(tweet),
		'contains_multiple_ques_excl_mark': contains_multiple_ques_excl_mark(tweet),
		'contains_second_pronoun': contains_second_pronoun(tweet),
		'contains_third_pronoun': contains_third_pronoun(tweet),
		'fraction_of_uppercase': fraction_of_uppercase(tweet),
		'url_count': url_count(tweet),
		'contains_user_mention': contains_user_mention(tweet),
		'contains_hashtag': contains_hashtag(tweet),
		'is_retweet': is_retweet(tweet),
		'is_reply': is_reply(tweet),
		'retweet_count': retweet_count(tweet),
		'reply_count': reply_count(tweet),
		'tweet_sentiment': tweet_sentiment(tweet),
		'tweeted_before_event': tweeted_before_event(tweet),
		'is_quoted_status': is_quoted_status(tweet),
		'vicinity_of_event': vicinity_of_event(tweet),
		'days_since_join': days_since_join(tweet),
		'status_count': status_count(tweet),
		'is_verified': is_verified(tweet),
		'non_empty_bio': non_empty_bio(tweet),
		'follower_count': follower_count(tweet),
		'friend_count': friend_count(tweet)
	}


# Returns dataframe from list of tweets
def compute_dataframe(tweets):
	data = []
	for tweet in tqdm(tweets):
		data.append(extract_features(tweet))
	
	return pd.DataFrame(data)


def saveToLTR(dataframe, file):
	datafile = open(file,'w+')
	count = 0
	for idx, row in dataframe.iterrows():
		count += 1
		if count == 500:
			break
		score,features = row['score'],[]
		for key,value in row.items():
			if key != 'score':
				features.append(value)

		line = str(score) + ' qid:1'
		for f in range(len(features)):
			line += ' ' + str(f) + ':' + str(features[f])
		line += '\n'
		datafile.write(line)


def evaluate(tweets):
	dataframe = compute_dataframe(tweets[500:])
	dataframe = dataframe.apply(lambda col: pd.factorize(col,sort=False)[0])	
	saveToLTR(dataframe, 'test.txt')


def main():
	tweets = []
	for tweet in db.tweets_sample.find():
		# Use annotated score for this
		tweet['score'] = random.randint(1,5)
		tweets.append(tweet)
	
	dataframe = compute_dataframe(tweets)
	dataframe = dataframe.apply(lambda col: pd.factorize(col,sort=False)[0])	

	dataframe.to_csv('tweets_ann.csv', sep='\t')

	saveToLTR(dataframe, 'train.txt')
	evaluate(tweets)



if __name__ == '__main__':
	main()

