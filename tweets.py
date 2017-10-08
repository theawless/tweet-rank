from collections import deque
from time import mktime, strptime

from utils import tokenize_text, compute_similarity_matrix

# not sure if we should add plurals
personal_pronouns = ["i", "me", "mine", "my"]

# taken from https://www.mltcreative.com/blog/social-media-minute-big-a-list-of-twitter-slang-and-definitions/
twitter_slangs = open("data/twitter-slangs.txt").readlines()


def tweet_time_to_timestamp(tweet_time):
    struct_time = strptime(tweet_time, '%a %b %d %H:%M:%S +0000 %Y')
    return mktime(struct_time) * 1000


def filter_tweets(tweets):
    filtered_tweets = []
    for tweet in tweets:
        if not any(word in tokenize_text(tweet["text"]) for word in personal_pronouns):
            if not any(word in tweet["text"] for word in twitter_slangs):
                filtered_tweets.append(tweet)
    return filtered_tweets


tweet_similarity_matrix = None


def get_tweet_similarity_matrix(tweets):
    global tweet_similarity_matrix
    if tweet_similarity_matrix is None:
        tweet_similarity_matrix = compute_similarity_matrix([tweet['text'] for tweet in tweets])
    return tweet_similarity_matrix


millisecond_in_hour = 60 * 60 * 1000


def tweets_window_by_nearby(tweets, interval=1):
    interval *= millisecond_in_hour
    nearby_tweets = deque()
    right_tweet_iter = iter(tweets)
    for tweet in tweets:
        tweet_time = int(tweet["timestamp_ms"])

        # remove from left
        while nearby_tweets:
            left_tweet = nearby_tweets[0]
            left_tweet_time = int(left_tweet["timestamp_ms"])
            if (tweet_time - left_tweet_time) / interval < 1:
                break
            nearby_tweets.popleft()

        # add to right
        right_tweet = next(right_tweet_iter, None)
        while right_tweet:
            right_tweet_time = int(right_tweet["timestamp_ms"])
            if (right_tweet_time - tweet_time) / interval > 1:
                break
            nearby_tweets.append(right_tweet)
            right_tweet = next(right_tweet_iter, None)
        yield tweet, nearby_tweets
        nearby_tweets = deque(nearby_tweets)


def tweets_chunk_by_time(tweets, interval=1):
    interval *= millisecond_in_hour
    start_time = int(tweets[0]["timestamp_ms"])
    hour = 0
    bucket = []
    for tweet in tweets:
        tweet_time = int(tweet["timestamp_ms"])
        new_hour = int((tweet_time - start_time) / interval)

        # next hour started
        if hour != new_hour:
            yield hour, bucket
            hour = new_hour
            bucket = []
        bucket.append(tweet)
    yield hour, bucket
