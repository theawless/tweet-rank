from utils import compute_similarity_matrix


def add_vertices(graph, items, genre):
    for item in items:
        graph.add_node(item["id_str"], content=item, genre=genre, score=0)


def add_item_item_edges(graph, items, similarity_threshold):
    similarity_matrix = compute_similarity_matrix([item['text'] for item in items])
    for i, j, w in zip(similarity_matrix.row, similarity_matrix.col, similarity_matrix.data):
        if i < j and w > similarity_threshold:
            graph.add_edge(items[i]["id_str"], items[j]["id_str"], weight=w)
            graph.add_edge(items[j]["id_str"], items[i]["id_str"], weight=w)


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


def add_tweet_user_edges(graph, tweets, users):
    pass


def add_doc_tweet_edges(graph, tweets, docs):
    pass
