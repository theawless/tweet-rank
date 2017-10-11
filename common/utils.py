import re
import string
from random import shuffle
from time import mktime, strptime

from nltk import word_tokenize


def tweet_time_to_timestamp(tweet_time):
    struct_time = strptime(tweet_time, '%a %b %d %H:%M:%S +0000 %Y')
    return mktime(struct_time) * 1000


def tokenize_text(text):
    # remove urls
    text = re.sub(r"http\S+", "", text)

    # tokenize
    text = text.translate(string.punctuation)
    words = word_tokenize(text)

    # remove weird characters
    words = [re.sub(r'\W+', "", word) for word in words]

    # remove known words
    words = [word for word in words if word not in ["rt", ""]]

    return words


millisecond_in_hour = 60 * 60 * 1000


def tweets_chunk_by_time(tweets, interval=1, sampled=1):
    interval *= millisecond_in_hour
    start_time = float(tweets[0]["timestamp_ms"])
    end_time = float(tweets[-1]["timestamp_ms"])
    bucket_size = int((end_time - start_time) / interval) + 1
    buckets = [[] for _ in range(bucket_size)]
    for tweet in tweets:
        tweet_time = float(tweet["timestamp_ms"])
        index = int((tweet_time - start_time) / interval)
        buckets[index].append(tweet)

    for bucket_index in range(len(buckets)):
        shuffle(buckets[bucket_index])
        right_tweet_index = int(len(buckets[bucket_index]) * sampled)
        buckets[bucket_index] = buckets[bucket_index][:right_tweet_index]
    return buckets
