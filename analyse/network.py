from analyse import tweets, users, docs
from analyse import tweets_similarity_matrix, docs_similarity_matrix
from analyse.utils import tweets_window_by_nearby


def add_tweet_vertices(graph):
    for tweet in tweets:
        graph.add_node(tweet["id_str"], content=tweet, tweet=True, score=0)


def add_user_vertices(graph):
    for user in users:
        graph.add_node(user["id_str"], content=user, user=True, score=0)


def add_doc_vertices(graph):
    for doc in docs:
        graph.add_node(doc["id_str"], content=doc, doc=True, score=0)


def add_tweet_tweet_edges(graph, threshold):
    for i, j, w in zip(tweets_similarity_matrix.row, tweets_similarity_matrix.col, tweets_similarity_matrix.data):
        if i < j and w > threshold:
            graph.add_edge(tweets[i]["id_str"], tweets[j]["id_str"], weight=w)
            graph.add_edge(tweets[j]["id_str"], tweets[i]["id_str"], weight=w)


def add_doc_doc_edges(graph, threshold):
    for i, j, w in zip(docs_similarity_matrix.row, docs_similarity_matrix.col, docs_similarity_matrix.data):
        if i < j and w > threshold:
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
    tweets_similarity_matrix_indexable = tweets_similarity_matrix.todok()
    for tweet_j_index, nearby_tweet_indexes in tweets_window_by_nearby(tweets):

        # build user tweet list
        user_tweet_index_dict = {}
        for nearby_tweet_index in nearby_tweet_indexes:
            user_id_str = tweets[nearby_tweet_index]["user"]["id_str"]
            if user_id_str not in user_tweet_index_dict:
                user_tweet_index_dict[user_id_str] = []
            user_tweet_index_dict[user_id_str].append(nearby_tweet_index)

        # check for max similarity
        for user_i_id_str, tweet_indexes in user_tweet_index_dict.items():
            similarity = max(tweets_similarity_matrix_indexable[tweet_j_index, tweet_i_index]
                             for tweet_i_index in tweet_indexes)
            if similarity >= threshold:
                tweet_j_id_str = tweets[tweet_j_index]["id_str"]
                graph.add_edge(user_i_id_str, tweet_j_id_str, weight=similarity)


def add_doc_tweet_edges(graph):
    pass
