from collections import deque

import scipy.sparse
from networkx import pagerank
from nltk import FreqDist
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

from common.utils import tokenize_text


def compute_pagerank(graph):
    ranks = pagerank(graph, weight="weight")
    for node_id in ranks.keys():
        graph.nodes[node_id]["score"] = ranks[node_id]


def compute_similarity_matrix(items):
    vectorizer = TfidfVectorizer(tokenizer=tokenize_text, stop_words='english')
    tfidf = vectorizer.fit_transform(items)
    sim_matrix = tfidf * tfidf.T

    # coo_matrix for fast iterations
    return scipy.sparse.coo_matrix(sim_matrix)


millisecond_in_hour = 60 * 60 * 1000


def tweets_window_by_nearby(tweets, interval=1):
    interval *= millisecond_in_hour
    nearby_tweet_indexes = deque()
    right_tweet_index_iter = iter(range(len(tweets)))
    for tweet_index in range(len(tweets)):
        tweet_time = int(tweets[tweet_index]["timestamp_ms"])

        # remove from left
        while nearby_tweet_indexes:
            left_tweet_index = nearby_tweet_indexes[0]
            left_tweet_time = int(tweets[left_tweet_index]["timestamp_ms"])
            if (tweet_time - left_tweet_time) / interval < 1:
                break
            nearby_tweet_indexes.popleft()

        # add to right
        right_tweet_index = next(right_tweet_index_iter, None)
        while right_tweet_index:
            right_tweet_time = int(tweets[right_tweet_index]["timestamp_ms"])
            if (right_tweet_time - tweet_time) / interval > 1:
                break
            nearby_tweet_indexes.append(right_tweet_index)
            right_tweet_index = next(right_tweet_index_iter, None)
        yield tweet_index, nearby_tweet_indexes
        nearby_tweet_indexes = deque(nearby_tweet_indexes)


def remove_stop_words(terms):
    return [term for term in terms if term not in stopwords.words('english')]


def find_top_terms(terms, number):
    distribution = FreqDist(terms)
    return distribution.most_common(number)
