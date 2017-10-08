from docs import get_doc_similarity_matrix
from tweets import tweets_window_by_nearby, get_tweet_similarity_matrix


def add_vertices(graph, items, genre):
    for item in items:
        graph.add_node(item["id_str"], content=item, genre=genre, score=0)


def add_tweet_tweet_edges(graph, tweets, threshold):
    similarity_matrix = get_tweet_similarity_matrix(tweets)
    for i, j, w in zip(similarity_matrix.row, similarity_matrix.col, similarity_matrix.data):
        if i < j and w > threshold:
            graph.add_edge(tweets[i]["id_str"], tweets[j]["id_str"], weight=w)
            graph.add_edge(tweets[j]["id_str"], tweets[i]["id_str"], weight=w)


def add_doc_doc_edges(graph, docs, threshold):
    similarity_matrix = get_doc_similarity_matrix(docs)
    for i, j, w in zip(similarity_matrix.row, similarity_matrix.col, similarity_matrix.data):
        if i < j and w > threshold:
            graph.add_edge(docs[i]["id_str"], docs[j]["id_str"], weight=w)
            graph.add_edge(docs[j]["id_str"], docs[i]["id_str"], weight=w)


def add_user_user_edges(graph, tweets):
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


def add_tweet_user_edges(graph, tweets, threshold):
    similarity_matrix = get_tweet_similarity_matrix(tweets)
    for tweet_j, nearby_tweets in tweets_window_by_nearby(tweets):
        tweet_j_id_str = tweet_j["id_str"]

        # build user tweet list
        user_tweet_dict = {}
        for nearby_tweet in nearby_tweets:
            user_id_str = nearby_tweet["user"]["id_str"]
            if user_id_str not in user_tweet_dict:
                user_tweet_dict[user_id_str] = []
            user_tweet_dict[user_id_str] = nearby_tweet["id_str"]

        # check for max similarity
        for user_i_id_str, tweet_id_strs in user_tweet_dict.items():
            max_similarity = max(similarity_matrix[tweet_j_id_str][tweet_i_id_str] for tweet_i_id_str in tweet_id_strs)
            if max_similarity >= threshold:
                graph[user_i_id_str][tweet_j_id_str] = max_similarity


def add_doc_tweet_edges(graph, tweets, docs):
    pass
