import networkx
import numpy
import sklearn.preprocessing
from tqdm import tqdm

import common.mongo
import common.utils
import network


def compute_pagerank(graph):
    ranks = networkx.pagerank_numpy(graph, weight="weight")
    for node_id in ranks.keys():
        graph.node[node_id]["score"] = ranks[node_id]


def compute_trihits(graph, L, max_iterations=50):
    print("computing trihits")

    # obtain initial scores vectors
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

    for t in range(len(network.tweets)):
        for n in graph.neighbors(network.tweets[t]["id_str"]):
            if graph.node[n]["label"] == "doc":
                W_dt[t][graph.node[n]["index"]] = graph[network.tweets[t]["id_str"]][n]['weight']
            if graph.node[n]["label"] == "user":
                W_ut[t][graph.node[n]["index"]] = graph[network.tweets[t]["id_str"]][n]['weight']

    progress = tqdm(range(max_iterations))
    for _ in progress:
        # compute new score for tweets
        Sd_t = sklearn.preprocessing.normalize(W_dt.dot(S_d), norm='l1', axis=0)
        Su_t = sklearn.preprocessing.normalize(W_ut.dot(S_u), norm='l1', axis=0)
        nS_t = (1 - L['dt'] - L['ut']) * S0_t + L['dt'] * Sd_t + L['ut'] * Su_t

        progress.set_description("error " + format(numpy.sum(numpy.absolute(nS_t - S_t)), '.32f'))

        # compute new score for users
        Su_t = sklearn.preprocessing.normalize(W_ut.T.dot(S_t), norm='l1', axis=0)
        nS_u = (1 - L['tu']) * S0_u + L['tu'] * Su_t

        # compute new score for docs
        Sd_t = sklearn.preprocessing.normalize(W_dt.T.dot(S_t), norm='l1', axis=0)
        nS_d = (1 - L['td']) * S0_d + L['td'] * Sd_t

        S_t = sklearn.preprocessing.normalize(nS_t, norm='l1', axis=0)
        S_d = sklearn.preprocessing.normalize(nS_d, norm='l1', axis=0)
        S_u = sklearn.preprocessing.normalize(nS_u, norm='l1', axis=0)

    # update score values for nodes in the graph
    for t in range(len(network.tweets)):
        graph.node[network.tweets[t]["id_str"]]['score'] = numpy.asscalar(S_t[t])
    for u in range(len(network.users)):
        graph.node[network.users[u]["id_str"]]['score'] = numpy.asscalar(S_u[u][0])
    for d in range(len(network.docs)):
        graph.node[network.docs[d]["id_str"]]['score'] = numpy.asscalar(S_d[d][0])


def compute_tweet_results(graph, top=20, redundancy=0.75):
    print("generating graph results")
    tweet_nodes = []
    for tweet in network.tweets:
        tweet_nodes.append(graph.node[tweet["id_str"]])
    tweet_nodes = sorted(tweet_nodes, reverse=True, key=lambda key: key["score"])

    # redundancy removal
    top_non_redundant_results = []
    for tweet_index in range(len(tweet_nodes)):
        if len(top_non_redundant_results) >= top:
            break
        similarities = []
        for last_tweet_index in range(tweet_index):
            similarities.append(network.t2t_similarity_matrix[tweet_nodes[tweet_index]["index"],
                                                              tweet_nodes[last_tweet_index]["index"]])
        if all(similarity < redundancy for similarity in similarities):
            top_non_redundant_results.append([network.tweets[tweet_nodes[tweet_index]["index"]]["text"],
                                              tweet_nodes[tweet_index]["score"]])
    return top_non_redundant_results


def compute_ndcg_at_k(graph, k=10):
    annotations_scores = {}
    for annotation in network.annotations:
        if graph.has_node(annotation["id_str"]):
            annotation["score"] = graph.node[annotation["id_str"]]["score"]
            if annotation["tag"] not in annotations_scores:
                annotations_scores[annotation["tag"]] = []
            annotations_scores[annotation["tag"]].append(annotation)
    ndcgs = {}
    for tag in annotations_scores.keys():
        annotations_scores[tag] = sorted(annotations_scores[tag], reverse=True, key=lambda x: x["score"])
        dcg = common.utils.compute_dcg([x["annotation"] for x in annotations_scores[tag][:k]])
        annotations_scores[tag] = sorted(annotations_scores[tag], reverse=True, key=lambda x: x["annotation"])
        idcg = common.utils.compute_dcg([x["annotation"] for x in annotations_scores[tag][:k]])
        ndcgs[tag] = dcg / idcg
    return ndcgs.items()
