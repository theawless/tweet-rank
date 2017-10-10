import re
import string
from time import mktime, strptime

from nltk import PorterStemmer, word_tokenize

stemmer = PorterStemmer()


def tweet_time_to_timestamp(tweet_time):
    struct_time = strptime(tweet_time, '%a %b %d %H:%M:%S +0000 %Y')
    return mktime(struct_time) * 1000


def tokenize_text(text):
    # remove urls
    text = re.sub(r"http\S+", "", text)

    # remove the punctuation
    text = text.translate(string.punctuation)

    # find word stems
    words = word_tokenize(text)
    return [stemmer.stem(item) for item in words]


millisecond_in_hour = 60 * 60 * 1000


def tweets_chunk_by_time(tweets, interval=1):
    interval *= millisecond_in_hour
    start_time = int(tweets[0]["timestamp_ms"])
    end_time = int(tweets[-1]["timestamp_ms"])
    bucket_size = int((end_time - start_time) / interval) + 1
    buckets = [[] for _ in range(bucket_size)]
    for tweet in tweets:
        tweet_time = int(tweet["timestamp_ms"])
        index = int((tweet_time - start_time) / interval)
        buckets[index].append(tweet)
    return buckets
