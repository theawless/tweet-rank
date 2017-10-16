import networkx
import numpy
import sklearn.preprocessing

import network


def compute_pagerank(graph):
    ranks = networkx.pagerank_numpy(graph, weight="weight")
    for node_id in ranks.keys():
        graph.node[node_id]["score"] = ranks[node_id]


def compute_trihits(graph, L, max_iterations=50):
    print("computing trihits")
    # Initialization
    k = 0

    # Obtain initial scores vectors of tweets, docs and users
    tweets_scores = [graph.node[tweet["id_str"]]['score'] for tweet in network.tweets]
    users_scores = [graph.node[user["id_str"]]['score'] for user in network.users]
    docs_scores = [graph.node[doc["id_str"]]['score'] for doc in network.docs]

    S0_t = numpy.asarray(tweets_scores).reshape(-1, 1)
    S0_u = numpy.asarray(users_scores).reshape(-1, 1)
    S0_d = numpy.asarray(docs_scores).reshape(-1, 1)

    S_t = numpy.asarray(tweets_scores).reshape(-1, 1)
    S_u = numpy.asarray(users_scores).reshape(-1, 1)
    S_d = numpy.asarray(docs_scores).reshape(-1, 1)

    # W_dt has rows of tweets and docs as columns
    W_dt = numpy.zeros(shape=(len(network.tweets), len(network.docs)))
    # W_ut has rows of tweets and users as columns
    W_ut = numpy.zeros(shape=(len(network.tweets), len(network.users)))

    docs_indexes = {network.docs[i]["id_str"]: i for i in range(len(network.docs))}
    users_indexes = {network.users[i]["id_str"]: i for i in range(len(network.users))}

    for t in range(len(network.tweets)):
        for n in graph.neighbors(network.tweets[t]["id_str"]):
            if "doc" in graph.node[n]:
                W_dt[t][docs_indexes[n]] = graph[network.tweets[t]["id_str"]][n]['weight']
            if "user" in graph.node[n]:
                W_ut[t][users_indexes[n]] = graph[network.tweets[t]["id_str"]][n]['weight']

    while k < max_iterations:
        # Compute new score for tweets
        Sd_t = sklearn.preprocessing.normalize(W_dt.dot(S_d), norm='l1', axis=0)
        Su_t = sklearn.preprocessing.normalize(W_ut.dot(S_u), norm='l1', axis=0)
        nS_t = (1 - L['dt'] - L['ut']) * S0_t + L['dt'] * Sd_t + L['ut'] * Su_t

        print(k, format(numpy.sum(numpy.absolute(nS_t - S_t)), '.32f'))

        # Compute new score for users
        Su_t = sklearn.preprocessing.normalize(W_ut.T.dot(S_t), norm='l1', axis=0)
        nS_u = (1 - L['tu']) * S0_u + L['tu'] * Su_t

        # Compute new score for docs
        Sd_t = sklearn.preprocessing.normalize(W_dt.T.dot(S_t), norm='l1', axis=0)
        nS_d = (1 - L['td']) * S0_d + L['td'] * Sd_t

        S_t = sklearn.preprocessing.normalize(nS_t, norm='l1', axis=0)
        S_d = sklearn.preprocessing.normalize(nS_d, norm='l1', axis=0)
        S_u = sklearn.preprocessing.normalize(nS_u, norm='l1', axis=0)

        k += 1

    # Update score values for nodes in the graph
    for t in range(len(network.tweets)):
        graph.node[network.tweets[t]["id_str"]]['score'] = numpy.asscalar(S_t[t])

    for u in range(len(network.users)):
        graph.node[network.users[u]["id_str"]]['score'] = numpy.asscalar(S_u[u][0])

    for d in range(len(network.docs)):
        graph.node[network.docs[d]["id_str"]]['score'] = numpy.asscalar(S_d[d][0])


def graph_results(graph, top=20, redundancy=0.75):
    print("generating graph results")
    tweets_scores = []
    for tweet in network.tweets:
        tweets_scores.append(graph.node[tweet["id_str"]])
    tweets_scores = sorted(tweets_scores, reverse=True, key=lambda key: key["score"])

    # do redundancy removal
    top_non_redundant_tweets_scores = []

    for tweet_index in range(len(tweets_scores)):
        if len(top_non_redundant_tweets_scores) >= top:
            break
        similarities = []
        for last_tweet_index in range(tweet_index):
            similarities.append(network.tweets_similarity_matrix[tweets_scores[tweet_index]["index"],
                                                                 tweets_scores[last_tweet_index]["index"]])
        if all(similarity < redundancy for similarity in similarities):
            top_non_redundant_tweets_scores.append([network.tweets[tweets_scores[tweet_index]["index"]]["text"],
                                                    tweets_scores[tweet_index]["score"]])
    dcg_at_k(graph, 10)
    return top_non_redundant_tweets_scores


def compute_idcg(annotations):
    idcg = 0.0
    a_sort = sorted(annotations, key=lambda x: x['annotation'], reverse=True)
    i = 1
    for s in a_sort:
        idcg += (numpy.power(2, int(s['annotation'])) - 1) / (numpy.log(i + 1, 2))
        i += 1
    return idcg


def dcg_at_k(graph, k):
    import common.mongo
    tweets_m_collection = common.mongo.database.tweets_m
    tweets_j_collection = common.mongo.database.tweets_j
    tweets_m = list(tweets_m_collection.find())
    tweets_j = list(tweets_j_collection.find())
    annotations_m = []
    annotations_j = []

    for tweet in tweets_m:
        annotation = common.mongo.annotations_collection.find_one({"tweet_id_str": tweet["id_str"]})
        try:
            annotation['score'] = graph.node[annotation["tweet_id_str"]]['score']
        except:
            continue
        annotations_m.append(annotation)

    for tweet in tweets_j:
        annotation = common.mongo.annotations_collection.find_one({"tweet_id_str": tweet["id_str"]})
        try:
            annotation['score'] = graph.node[annotation["tweet_id_str"]]['score']
        except:
            continue
        annotations_j.append(annotation)

    annotations_m = sorted(annotations_m, reverse=True, key=lambda x: x["score"])[:k + 1]
    dm, i = 0, 1
    for annotation in annotations_m:
        annotation_score = int(annotation["annotation"])
        dm += (numpy.power(2, annotation_score) - 1) / (numpy.log(i + 1, 2))
        i += 1

    annotations_j = sorted(annotations_j, reverse=True, key=lambda x: x["score"])[:k + 1]
    dj, i = 0, 1
    for annotation in annotations_j:
        annotation_score = int(annotation["annotation"])
        dj += (numpy.power(2, annotation_score) - 1) / (numpy.log(i + 1, 2))
        i += 1

    print("DCG: ", dm / compute_idcg(annotations_m), dj / compute_idcg(annotations_j))
