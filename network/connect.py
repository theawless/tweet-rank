import sys

import numpy
import scipy.sparse
import sklearn.feature_extraction.text
import sklearn.metrics.pairwise

import common.tweets
import common.utils
import network


def add_tweet_vertices(graph):
    print("adding tweet nodes")
    for i in range(len(network.tweets)):
        graph.add_node(network.tweets[i]["id_str"], index=i, tweet=True, score=0)


def add_user_vertices(graph):
    print("adding user nodes")
    for i in range(len(network.users)):
        graph.add_node(network.users[i]["id_str"], index=i, user=True, score=0)


def add_doc_vertices(graph):
    print("adding doc nodes")
    for i in range(len(network.docs)):
        graph.add_node(network.docs[i]["id_str"], index=i, doc=True, score=0)


def add_tweet_tweet_edges(graph, threshold):
    print("adding tweet tweet nodes")
    count = 0
    for r, c in zip(*(network.tweets_similarity_matrix > threshold).nonzero()):
        count += 1
        sys.stdout.write('\rCount: %d' % count)
        sys.stdout.flush()
        w = network.tweets_similarity_matrix[r, c]
        if r < c and w > threshold:
            graph.add_edge(network.tweets[r]["id_str"], network.tweets[c]["id_str"], weight=w)
            graph.add_edge(network.tweets[c]["id_str"], network.tweets[r]["id_str"], weight=w)


def add_doc_doc_edges(graph, threshold):
    print("\nadding doc doc edges")
    count = 0
    for r, c in zip(*(network.docs_similarity_matrix > threshold).nonzero()):
        count += 1
        sys.stdout.write('\rCount: %d' % count)
        sys.stdout.flush()
        w = network.docs_similarity_matrix[r, c]
        if r < c and w > threshold:
            graph.add_edge(network.docs[r]["id_str"], network.docs[c]["id_str"], weight=w)
            graph.add_edge(network.docs[c]["id_str"], network.docs[r]["id_str"], weight=w)


def add_user_user_edges(graph):
    print("\nadding user user edges")
    for tweet in network.tweets:
        # author
        user_i = tweet["user"]["id_str"]
        user_js = []

        # retweet
        if "retweeted_status" in tweet:
            user_j = tweet["retweeted_status"]["user"]["id_str"]
            if user_i != user_j:
                user_js.append(user_j)

        # reply
        user_j = tweet["in_reply_to_user_id_str"]
        if user_j is not None:
            if user_i != user_j:
                user_js.append(user_j)

        # mentions
        for mention in tweet["entities"]["user_mentions"]:
            if user_i != mention["id_str"]:
                user_js.append(mention["id_str"])

        for user_j in user_js:
            if not graph.has_edge(user_i, user_j):
                graph.add_edge(user_i, user_j, weight=0)
            graph[user_i][user_j]["weight"] += 1
    return graph


def add_tweet_user_edges(graph, threshold):
    print("adding tweet user edges")
    count = 0
    for tweet_j_index, nearby_tweet_indexes in common.tweets.tweets_window_by_nearby(network.tweets):
        count += 1
        sys.stdout.write('\rCount: %d' % count)
        sys.stdout.flush()

        # implicit edge
        tweet_j = network.tweets[tweet_j_index]
        graph.add_edge(tweet_j["id_str"], tweet_j["user"]["id_str"], weight=1)

        # build user tweet list
        user_tweet_index_dict = {}
        for nearby_tweet_index in nearby_tweet_indexes:
            user_id_str = network.tweets[nearby_tweet_index]["user"]["id_str"]
            if user_id_str not in user_tweet_index_dict:
                user_tweet_index_dict[user_id_str] = []
            user_tweet_index_dict[user_id_str].append(nearby_tweet_index)

        # check for max similarity
        for user_i_id_str, tweet_indexes in user_tweet_index_dict.items():
            if tweet_j["user"]["id_str"] == user_i_id_str:
                continue
            similarity = max(network.tweets_similarity_matrix[tweet_j_index, tweet_i_index]
                             for tweet_i_index in tweet_indexes)
            if similarity > threshold:
                tweet_j_id_str = tweet_j["id_str"]
                graph.add_edge(tweet_j_id_str, user_i_id_str, weight=1)


def add_doc_tweet_edges(graph, threshold):
    print("adding doc tweet edges")
    tweet_texts = [tweet['text'] for tweet in network.tweets]

    tfidf_transformer = sklearn.feature_extraction.text.TfidfTransformer()
    vectorizer = sklearn.feature_extraction.text.CountVectorizer(tokenizer=common.utils.tokenize_text,
                                                                 stop_words='english')
    tweets_matrix = vectorizer.fit_transform(tweet_texts)
    tfidf_transformer.fit(tweets_matrix)
    tfidf_transformer.transform(tweets_matrix)

    results = []
    for doc in network.docs:
        doc_text = doc['text']
        doc_vector = vectorizer.transform([doc_text])

        tfidf_transformer.fit(doc_vector)
        tfidf_doc = tfidf_transformer.transform(doc_vector)

        result = numpy.array([numpy.asscalar(s) for s in sklearn.metrics.pairwise.cosine_similarity(tweets_matrix,
                                                                                                    tfidf_doc)])
        results.append(result)

    doc_tweet_matrix = scipy.sparse.csr_matrix(results)
    count = 0
    for r, c in zip(*(doc_tweet_matrix > threshold).nonzero()):
        count += 1
        sys.stdout.write('\rCount: %d' % count)
        sys.stdout.flush()
        w = doc_tweet_matrix[r, c]
        graph.add_edge(network.docs[r]["id_str"], network.tweets[c]["id_str"], weight=w)
        graph.add_edge(network.tweets[c]["id_str"], network.docs[r]["id_str"], weight=w)
