import pymongo
from pymongo import MongoClient
from bson.json_util import loads
import matplotlib.pyplot as plt

client = MongoClient()
db = client['vegas']

tweets = []

def loadTweets():
	for tweet in db.tweets.find().sort('created_at', pymongo.ASCENDING):
		tweets.append(tweet)

def isSpam(tweet):
	return False

def spamPercent(s):
	total = s['spam'] + s['non_spam']
	return (float(s['non_spam'])/total)*100

# interval is in terms of seconds
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

	    # create a bin with the data
		tweet_bins.append([bin_start, {'spam': int(isSpam(tweet)), 'non_spam': int(not isSpam(tweet))}])

	print(tweet_bins)
	
	x = [t[0] for t in tweet_bins]
	y = [spamPercent(t[1]) for t in tweet_bins]

	plt.xlabel('Time')
	plt.ylabel('% Spam')
	plt.title('Spam Distribution')

	plt.hist(x, len(x), weights=y)
	plt.show()
	
# def insertTweets():
# 	with open('tweets.json') as data:
# 		sliced_tweets = []
# 		tweets = data.readlines()
# 		for tweet in tweets[:1000]:
# 			sliced_tweets.append(loads(tweet))

# 		db.tweets.insert_many(sliced_tweets)


if __name__ == '__main__':
	loadTweets()
	spamDistribution(interval=1)	