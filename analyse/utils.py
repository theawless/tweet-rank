import numpy
from networkx import pagerank_numpy
from numpy import asarray, zeros, absolute, asscalar
from sklearn.preprocessing import normalize

from analyse import docs, tweets, users, tweets_similarity_matrix


def compute_pagerank(graph):
    ranks = pagerank_numpy(graph, weight="weight")
    for node_id in ranks.keys():
        graph.node[node_id]["score"] = ranks[node_id]


def compute_trihits(graph, L, max_iterations=50):
    # Initialization
    k = 0

    # Obtain initial scores vectors of tweets, docs and users
    tweets_scores = [graph.node[tweet["id_str"]]['score'] for tweet in tweets]
    users_scores = [graph.node[user["id_str"]]['score'] for user in users]
    docs_scores = [graph.node[doc["id_str"]]['score'] for doc in docs]

    S0_t = asarray(tweets_scores).reshape(-1, 1)
    S0_u = asarray(users_scores).reshape(-1, 1)
    S0_d = asarray(docs_scores).reshape(-1, 1)

    S_t = asarray(tweets_scores).reshape(-1, 1)
    S_u = asarray(users_scores).reshape(-1, 1)
    S_d = asarray(docs_scores).reshape(-1, 1)

    # W_dt has rows of tweets and docs as columns
    W_dt = zeros(shape=(len(tweets), len(docs)))
    # W_ut has rows of tweets and users as columns
    W_ut = zeros(shape=(len(tweets), len(users)))

    docs_indexes = {docs[i]["id_str"]: i for i in range(len(docs))}
    users_indexes = {users[i]["id_str"]: i for i in range(len(users))}

    for t in range(len(tweets)):
        p = list(graph.neighbors(tweets[t]["id_str"]))
        for n in graph.neighbors(tweets[t]["id_str"]):
            if "doc" in graph.node[n]:
                W_dt[t][docs_indexes[n]] = graph[tweets[t]["id_str"]][n]['weight']
            if "user" in graph.node[n]:
                W_ut[t][users_indexes[n]] = graph[tweets[t]["id_str"]][n]['weight']

    while k < max_iterations:
        # Compute new score for tweets
        Sd_t = normalize(W_dt.dot(S_d), norm='l1', axis=0)
        Su_t = normalize(W_ut.dot(S_u), norm='l1', axis=0)
        nS_t = (1 - L['dt'] - L['ut']) * S0_t + L['dt'] * Sd_t + L['ut'] * Su_t

        print(k, format(numpy.sum(absolute(nS_t - S_t)), '.32f'))

        # Compute new score for users
        Su_t = normalize(W_ut.T.dot(S_t), norm='l1', axis=0)
        nS_u = (1 - L['tu']) * S0_u + L['tu'] * Su_t

        # Compute new score for docs
        Sd_t = normalize(W_dt.T.dot(S_t), norm='l1', axis=0)
        nS_d = (1 - L['td']) * S0_d + L['td'] * Sd_t

        S_t = normalize(nS_t, norm='l1', axis=0)
        S_d = normalize(nS_d, norm='l1', axis=0)
        S_u = normalize(nS_u, norm='l1', axis=0)

        k += 1

    # Update score values for nodes in the graph
    for t in range(len(tweets)):
        graph.node[tweets[t]["id_str"]]['score'] = asscalar(S_t[t])

    for u in range(len(users)):
        graph.node[users[u]["id_str"]]['score'] = asscalar(S_u[u][0])

    for d in range(len(docs)):
        graph.node[docs[d]["id_str"]]['score'] = asscalar(S_d[d][0])


def graph_results(graph, top=20, redundancy=0.85):
    tweets_scores = []
    for tweet in tweets:
        tweets_scores.append(graph.node[tweet["id_str"]])
    tweets_scores = sorted(tweets_scores, reverse=True, key=lambda key: key["score"])

    # do redundancy removal
    top_non_redundant_tweets_scores = []

    last_tweet_index = 0
    for tweet_index in range(1, len(tweets_scores)):
        if len(top_non_redundant_tweets_scores) >= top:
            break
        similarity = tweets_similarity_matrix[tweets_scores[tweet_index]["index"],
                                              tweets_scores[last_tweet_index]["index"]]
        if similarity < redundancy:
            last_tweet_index = tweet_index
            top_non_redundant_tweets_scores.append(tweets_scores[tweet_index])
    return top_non_redundant_tweets_scores
