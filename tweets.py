from utils import tokenize_text

# not sure if we should add plurals
personal_pronouns = ["i", "me", "mine", "my"]

# taken from https://www.mltcreative.com/blog/social-media-minute-big-a-list-of-twitter-slang-and-definitions/
twitter_slangs = open("data/twitter-slangs.txt").readlines()


def filter_tweets(tweets):
    filtered_tweets = []
    for tweet in tweets:
        if not any(word in tokenize_text(tweet["text"]) for word in personal_pronouns):
            if not any(word in tweet["text"] for word in twitter_slangs):
                filtered_tweets.append(tweet)
    return filtered_tweets


def distribute_tweets(tweets, interval=1):
    interval *= 60 * 60 * 1000
    start_time = int(tweets[0]["timestamp_ms"])
    end_time = int(tweets[-1]["timestamp_ms"])
    bucket_size = int((end_time - start_time) / interval) + 1
    buckets = [[]] * bucket_size
    for tweet in tweets:
        tweet_time = int(tweet["timestamp_ms"])
        index = int((tweet_time - start_time) / interval)
        buckets[index].append(tweet)
    return buckets
