from analyse import tweets, users, docs, docs_similarity_matrix
from analyse import tweets_similarity_matrix
from common.tweets import tweets_window_by_nearby


def add_tweet_vertices(graph):
    for i in range(len(tweets)):
        graph.add_node(tweets[i]["id_str"], index=i, tweet=True, score=0)


def add_user_vertices(graph):
    for i in range(len(users)):
        graph.add_node(users[i]["id_str"], index=i, user=True, score=0)


def add_doc_vertices(graph):
    for i in range(len(docs)):
        graph.add_node(docs[i]["id_str"], index=i, doc=True, score=0)


def add_tweet_tweet_edges(graph, threshold):
    for i in range(len(tweets)):
        for j in range(len(tweets)):
            w = tweets_similarity_matrix[i, j]
            if tweets[i]["id_str"] != tweets[j]["id_str"] and w > threshold:
                graph.add_edge(tweets[i]["id_str"], tweets[j]["id_str"], weight=w)
                graph.add_edge(tweets[j]["id_str"], tweets[i]["id_str"], weight=w)


def add_doc_doc_edges(graph, threshold):
    for i in range(len(docs)):
        for j in range(len(docs)):
            w = docs_similarity_matrix[i, j]
            if docs[i]["id_str"] != docs[j]["id_str"] and w > threshold:
                graph.add_edge(docs[i]["id_str"], docs[j]["id_str"], weight=w)
                graph.add_edge(docs[j]["id_str"], docs[i]["id_str"], weight=w)


def add_user_user_edges(graph):
    for tweet in tweets:
        # author
        user_i = tweet["user"]["id_str"]
        user_js = []

        # retweet
        if "retweeted_status" in tweet:
            user_j = tweet["retweeted_status"]["user"]["id_str"]
            user_js.append(user_j)

        # reply
        user_j = tweet["in_reply_to_user_id_str"]
        if user_j is not None:
            user_js.append(user_j)

        # mentions
        for mention in tweet["entities"]["user_mentions"]:
            user_js.append(mention["id_str"])

        for user_j in user_js:
            if not graph.has_edge(user_i, user_j):
                graph.add_edge(user_i, user_j, weight=0)
            graph[user_i][user_j]["weight"] += 1
    return graph


def add_tweet_user_edges(graph, threshold):
    for tweet_j_index, nearby_tweet_indexes in tweets_window_by_nearby(tweets):
        # implicit edge
        tweet_j = tweets[tweet_j_index]
        if not graph.has_edge(tweet_j["id_str"], tweet_j["user"]["id_str"]):
            graph.add_edge(tweet_j["id_str"], tweet_j["user"]["id_str"], weight=0)
        graph[tweet_j["id_str"]][tweet_j["user"]["id_str"]]["weight"] += 1

        # build user tweet list
        user_tweet_index_dict = {}
        for nearby_tweet_index in nearby_tweet_indexes:
            user_id_str = tweets[nearby_tweet_index]["user"]["id_str"]
            if user_id_str not in user_tweet_index_dict:
                user_tweet_index_dict[user_id_str] = []
            user_tweet_index_dict[user_id_str].append(nearby_tweet_index)

        # check for max similarity
        for user_i_id_str, tweet_indexes in user_tweet_index_dict.items():
            similarity = max(tweets_similarity_matrix[tweet_j_index, tweet_i_index]
                             for tweet_i_index in tweet_indexes)
            if similarity >= threshold:
                tweet_j_id_str = tweet_j["id_str"]
                if not graph.has_edge(tweet_j_id_str, user_i_id_str):
                    graph.add_edge(tweet_j_id_str, user_i_id_str, weight=0)
                graph[tweet_j_id_str][user_i_id_str]["weight"] += 1


def add_doc_tweet_edges(graph, threshold):
    return
