import pymongo
from pymongo import MongoClient
from bson.json_util import loads
import matplotlib.pyplot as plt

client = MongoClient()
db = client['vegas']
tweets = []
tweet_ids = set()

def loadTweets():
	for tweet in db.tweets.find().sort('timestamp_ms', pymongo.ASCENDING):
		if tweet['id'] not in tweet_ids:
			tweets.append(tweet)
			tweet_ids.add(tweet['id'])

# TODO: Implement filtering
def isSpam(tweet):
	return False

def spamPercent(s):
	total = s['spam'] + s['non_spam']
	return (float(s['spam'])/total)*100

# TODO: Show hours on time axis
# Interval is in terms of seconds
# Default interval is 60 seconds
def spamDistribution(interval=60):
	tweet_bins = []
	INTERVAL = interval*1000

	bin_start = int(tweets[0]['timestamp_ms'])
	tweet_bins.append([bin_start, {'spam': 0, 'non_spam': 0}])

	for tweet in tweets[:10]:
		tweet_time = int(tweet['timestamp_ms'])

		# If the tweet belongs to this bin, append it into the bin
		if tweet_time < bin_start + INTERVAL:
			if isSpam(tweet):
				tweet_bins[-1][1]['spam'] += 1
			else:
				tweet_bins[-1][1]['non_spam'] += 1
			continue

		# Otherwise, create new empty bins until this tweet fits into a bin
		bin_start += INTERVAL
		while tweet_time > bin_start + INTERVAL:	
			tweet_bins.append([bin_start, {'spam': 0, 'non_spam': 0}])
			bin_start += INTERVAL

	    # create a bin with the tweet
		tweet_bins.append([bin_start, {'spam': int(isSpam(tweet)), 'non_spam': int(not isSpam(tweet))}])

	print(tweet_bins)
	
	x = [t[0] for t in tweet_bins]
	y = [spamPercent(t[1]) for t in tweet_bins]

	plt.xlabel('Time')
	plt.ylabel('% Spam')
	plt.title('Spam Distribution')

	plt.hist(x, len(x), weights=y)
	plt.show()

def topTenHashTags():
	hash_tags = {}
	for tweet in tweets:
		if 'entities' in tweet:
			for hash_tag in tweet['entities']['hashtags']:
				h = hash_tag['text']
				if h in hash_tags:
					hash_tags[h] += 1
				else:
					hash_tags[h] = 1

	return sorted(hash_tags.items(), key=lambda x:x[1], reverse=True)[:10]


def insertTweets():
	with open('../data/tweets.json') as data:
		sliced_tweets = []
		tweets = data.readlines()
		for tweet in tweets[:1000]:
			sliced_tweets.append(loads(tweet))

		db.tweets.insert_many(sliced_tweets)

if __name__ == '__main__':
	loadTweets()
	print(len(tweets))
	# spamDistribution(interval=1)
	# print(topTenHashTags())