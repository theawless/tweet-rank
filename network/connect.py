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


def add_tweet_tweet_edges(graph, similarity_threshold, geo_signal_factor, common_neighbour_factor):
    print("adding tweet tweet edges")
    count = 0
    for r, c in tqdm(zip(*(network.t2t_similarity_matrix > similarity_threshold).nonzero())):
        if r != c:
            count += 1
            w = (1 - geo_signal_factor - common_neighbour_factor) * network.t2t_similarity_matrix[r, c]
            graph.add_edge(network.tweets[r]["id_str"], network.tweets[c]["id_str"], label="similarity", weight=w)
    print(count)


def add_tweet_tweet_geo_signals(graph, geo_signal_factor, vicinity_radius):
    print("adding geo signals")
    for i in tqdm(range(len(network.tweets))):
        for j in range(i + 1):
            if (common.tweets.vicinity_of_event(network.tweets[i], vicinity_radius) and
                    common.tweets.vicinity_of_event(network.tweets[j], vicinity_radius)):
                t1_id_str, t2_id_str = network.tweets[i]["id_str"], network.tweets[j]["id_str"]
                if not graph.has_edge(t1_id_str, t2_id_str):
                    graph.add_edge(t1_id_str, t2_id_str, label="", weight=0)
                    graph.add_edge(t2_id_str, t1_id_str, label="", weight=0)
                graph[t1_id_str][t2_id_str]["label"] += "geo"
                graph[t2_id_str][t1_id_str]["label"] += "geo"
                graph[t1_id_str][t2_id_str]["weight"] += geo_signal_factor
                graph[t2_id_str][t1_id_str]["weight"] += geo_signal_factor


def add_tweet_doc_tweet_common_edges(graph, similarity_threshold, common_neighbour_factor):
    print("adding tweet tweet edges between tweets with common doc neighbour")
    count = 0
    doc_tweets = {}
    for r, c in zip(*(network.t2d_similarity_matrix > similarity_threshold).nonzero()):
        if network.docs[r]["id_str"] not in doc_tweets:
            doc_tweets[network.docs[r]["id_str"]] = []
        doc_tweets[network.docs[r]["id_str"]].append(network.tweets[c]["id_str"])

    for doc, tweets in doc_tweets.items():
        for tweet1 in tweets:
            for tweet2 in tweets:
                if not graph.has_edge(tweet1, tweet2):
                    graph.add_edge(tweet1, tweet2, label="common", weight=common_neighbour_factor)
                    graph.add_edge(tweet2, tweet1, label="common", weight=common_neighbour_factor)
                    count += 1
                elif "common" not in graph[tweet1][tweet2]["label"]:
                    graph[tweet1][tweet2]["label"] += "common"
                    graph[tweet2][tweet1]["label"] += "common"
                    graph[tweet1][tweet2]["weight"] += common_neighbour_factor
                    graph[tweet2][tweet1]["weight"] += common_neighbour_factor
                    count += 1
    print(count)


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
