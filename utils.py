import re
import string

import scipy.sparse
from nltk import PorterStemmer, word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer


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


def tokenize(text):
    text = text.lower()

    # remove urls
    text = re.sub(r"http\S+", "", text)

    # remove the punctuation
    text = text.translate(string.punctuation)

    # find word stems
    words = word_tokenize(text)
    return [stemmer.stem(item) for item in words]


stemmer = PorterStemmer()
vectorizer = TfidfVectorizer(tokenizer=tokenize, stop_words='english')

def compute_tweet_sim_matrix(tweets):
    tfidf = vectorizer.fit_transform(tweets)
    sim_matrix = tfidf * tfidf.T

    # Return coo_matrix for fast iterations
    return scipy.sparse.coo_matrix(sim_matrix)


def filter_tweets(tweets):
    # remove spam, and tweets with slang/pronouns
    return tweets