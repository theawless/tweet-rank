from collections import deque

import networkx as nx
import numpy as np
import scipy.sparse
from nltk import FreqDist
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

from common.utils import tokenize_text


def compute_pagerank(graph):
    ranks = nx.pagerank(graph, weight="weight")
    for node_id in ranks.keys():
        graph.nodes[node_id]["score"] = ranks[node_id]


def compute_trihits(graph, L, max_iterations=50):
    # Initialization
    k = 0

    tweet_ids = nx.get_node_attributes(graph, 'tweet').keys()
    doc_ids = nx.get_node_attributes(graph, 'doc').keys()
    user_ids = nx.get_node_attributes(graph, 'user').keys()

    # Obtain initial scores of tweets, docs and users
    # Note, they are all vectors
    S0_t = np.asarray([graph[tweet_id]['score'] for tweet_id in tweet_ids]).reshape(-1, 1)
    S0_u = np.asarray([graph[user_id]['score'] for user_id in user_ids]).reshape(-1, 1)
    S0_d = np.asarray([graph[doc_id]['score'] for doc_id in doc_ids]).reshape(-1, 1)

    S_t = np.asarray([graph[tweet_id]['score'] for tweet_id in tweet_ids]).reshape(-1, 1)
    S_u = np.asarray([graph[user_id]['score'] for user_id in user_ids]).reshape(-1, 1)
    S_d = np.asarray([graph[doc_id]['score'] for doc_id in doc_ids]).reshape(-1, 1)

    # W_dt has rows of tweets and docs as columns
    W_dt = np.zeros(shape=(len(tweet_ids), len(doc_ids)))
    docs = {doc_ids[i]: i for i in range(len(doc_ids))}
    for t in range(len(tweet_ids)):
        for n in graph.neighbors(tweet_ids[t]):
            if graph[n]['doc']:
                W_dt[t][docs[n]] = graph[t][n]['weight']

    # W_ut has rows of tweets and users as columns
    W_ut = np.zeros(shape=(len(tweet_ids), len(user_ids)))
    users = {user_ids[i]: i for i in range(len(user_ids))}
    for t in range(len(tweet_ids)):
        for n in graph.neighbors(tweet_ids[t]):
            if graph[n]['user']:
                W_dt[t][users[n]] = graph[t][n]['weight']

    while k < max_iterations:
        # Compute new score for tweets
        Sd_t = normalize(W_dt * S_d, norm='l1', axis=0)
        Su_t = normalize(W_ut * S_u, norm='l1', axis=0)
        nS_t = (1 - L['dt'] - L['ut']) * S0_t + L['dt'] * Sd_t + L['ut'] * Su_t

        # Compute new score for users
        Su_t = normalize(W_ut.T * S_t, norm='l1', axis=0)
        nS_u = (1 - L['tu']) * S0_u + L['tu'] * Su_t

        # Compute new score for docs
        Sd_t = normalize(W_dt.T * S_t, norm='l1', axis=0)
        nS_d = (1 - L['td']) * S0_d + L['td'] * Sd_t

        S_t = normalize(nS_t, norm='l1', axis=0)
        S_d = normalize(nS_d, norm='l1', axis=0)
        S_u = normalize(nS_u, norm='l1', axis=0)

        # diff =  np.sum(np.absolute(nS_t - S_t))
        k += 1

    # Update score values for nodes in the graph
    for t in range(len(tweet_ids)):
        graph[tweet_ids[t]]['score'] = S_t[t]

    for u in range(len(user_ids)):
        graph[tweet_ids[u]]['score'] = S_t[u]

    for d in range(len(doc_ids)):
        graph[tweet_ids[d]]['score'] = S_t[d]


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
