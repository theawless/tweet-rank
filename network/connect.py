import networkx
from tqdm import tqdm

import common.tweets
import common.utils
import network


def add_tweet_vertices(graph):
    print("adding tweet nodes")
    for i in tqdm(range(len(network.tweets))):
        graph.add_node(network.tweets[i]["id_str"], index=i, label="tweet", score=0)


def add_user_vertices(graph):
    print("adding user nodes")
    for i in tqdm(range(len(network.users))):
        graph.add_node(network.users[i]["id_str"], index=i, label="user", score=0)


def add_doc_vertices(graph):
    print("adding doc nodes")
    for i in tqdm(range(len(network.docs))):
        graph.add_node(network.docs[i]["id_str"], index=i, label="doc", score=0)


def add_tweet_tweet_edges(graph, similarity_threshold, tweets_similarity_factor):
    print("adding tweet tweet edges")
    for r, c in tqdm(zip(*(network.t2t_similarity_matrix > similarity_threshold).nonzero())):
        if r != c:
            w = tweets_similarity_factor * network.t2t_similarity_matrix[r, c]
            graph.add_edge(network.tweets[r]["id_str"], network.tweets[c]["id_str"], label="similarity", weight=w)


def add_tweet_tweet_geo_signals(graph, vicinity_radius, tweets_similarity_factor, common_neighbour_factor):
    print("adding geo signals")
    for i in range(len(network.tweets)):
        for j in range(i + 1):
            if (common.tweets.vicinity_of_event(network.tweets[i], vicinity_radius) and
                    common.tweets.vicinity_of_event(network.tweets[j], vicinity_radius)):
                v = 1 - tweets_similarity_factor - common_neighbour_factor
                t1_id_str, t2_id_str = network.tweets[i]["id_str"], network.tweets[j]["id_str"]
                if not graph.has_edge(t1_id_str, t2_id_str):
                    graph.add_edge(t1_id_str, t2_id_str, label="", weight=0)
                    graph.add_edge(t2_id_str, t1_id_str, label="", weight=0)
                graph[t1_id_str][t2_id_str]["label"] += "geo"
                graph[t2_id_str][t1_id_str]["label"] += "geo"
                graph[t1_id_str][t2_id_str]["weight"] += v
                graph[t2_id_str][t1_id_str]["weight"] += v


def add_tweet_doc_tweet_common_edges(t2t_graph, d2d_graph, similarity_threshold, common_neighbour_factor):
    print("adding tweet tweet edges between tweets with common doc neighbour")
    # hack! do not save these edges to graph because the graph is still homogeneous at this step
    dt_graph = networkx.union(t2t_graph, d2d_graph)
    add_doc_tweet_edges(dt_graph, similarity_threshold)

    # doc to doc edges have not been made yet, hence all neighbours of docs are tweets
    for i in range(len(network.docs)):
        d_id_str = network.docs[i]["id_str"]
        for t1_id_str in dt_graph.neighbors(d_id_str):
            for t2_id_str in dt_graph.neighbors(d_id_str):
                if t1_id_str != t2_id_str:
                    w1 = dt_graph[d_id_str][t1_id_str]["weight"]
                    w2 = dt_graph[d_id_str][t2_id_str]["weight"]
                    v = common_neighbour_factor * (w1 * w2) / (w1 + w2)
                    if not t2t_graph.has_edge(t1_id_str, t2_id_str):
                        t2t_graph.add_edge(t1_id_str, t2_id_str, label="", weight=0)
                    t2t_graph[t1_id_str][t2_id_str]["label"] += "common"
                    t2t_graph[t1_id_str][t2_id_str]["weight"] += v


def add_doc_doc_edges(graph, threshold):
    print("adding doc doc edges")
    for r, c in tqdm(zip(*(network.d2d_similarity_matrix > threshold).nonzero())):
        if r != c:
            w = network.d2d_similarity_matrix[r, c]
            graph.add_edge(network.docs[r]["id_str"], network.docs[c]["id_str"], label="similarity", weight=w)


def add_user_user_edges(graph):
    print("adding user user edges")
    for tweet in tqdm(network.tweets):
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
                graph.add_edge(user_i, user_j, label="interaction", weight=0)
            graph[user_i][user_j]["weight"] += 1
    return graph


def add_tweet_user_edges(graph, threshold):
    print("adding tweet user edges")
    for tweet_j_index, nearby_tweet_indexes in tqdm(common.tweets.window_by_nearby(network.tweets)):
        # implicit edge
        tweet_j = network.tweets[tweet_j_index]
        graph.add_edge(tweet_j["id_str"], tweet_j["user"]["id_str"], label="direct", weight=1)
        graph.add_edge(tweet_j["user"]["id_str"], tweet_j["id_str"], label="direct", weight=1)

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
            similarity = max(network.t2t_similarity_matrix[tweet_j_index, tweet_i_index]
                             for tweet_i_index in tweet_indexes)
            if similarity > threshold:
                tweet_j_id_str = tweet_j["id_str"]
                graph.add_edge(tweet_j_id_str, user_i_id_str, label="indirect", weight=1)
                graph.add_edge(user_i_id_str, tweet_j_id_str, label="indirect", weight=1)


def add_doc_tweet_edges(graph, similarity_threshold):
    print("adding doc tweet edges")
    for r, c in zip(*(network.t2d_similarity_matrix > similarity_threshold).nonzero()):
        w = network.t2d_similarity_matrix[r, c]
        graph.add_edge(network.docs[r]["id_str"], network.tweets[c]["id_str"], label="similarity", weight=w)
        graph.add_edge(network.tweets[c]["id_str"], network.docs[r]["id_str"], label="similarity", weight=w)
