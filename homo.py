from igraph import Graph

from utils import cosine_similarity


def init_tweet_graph(tweets):
    t2t_graph = Graph()
    add_vertices(t2t_graph, tweets, "tweet")
    add_tweet_edges(t2t_graph, tweets)
    t2t_graph.personalized_pagerank(directed=False, weights="weight")
    return t2t_graph


def init_user_graph(tweets, users):
    u2u_graph = Graph()
    add_vertices(u2u_graph, users, "user")
    add_user_edges(u2u_graph, tweets)
    u2u_graph.personalized_pagerank(directed=True, weights="weight")
    return u2u_graph


def init_web_graph():
    pass


def add_vertices(graph, items, genre):
    graph.add_vertices(len(items))
    for item, vertex in zip(items, graph.vs):
        vertex["name"] = item["id_str"]
        vertex["data"] = item
        vertex["genre"] = genre


def add_user_edges(graph, tweets):
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
            if not graph.are_connected(user_i, user_j):
                graph.add_edge(user_i, user_j, weight=0)
            edge_id = graph.get_eid(user_i, user_j, directed=True)
            graph.es[edge_id]["weight"] += 1
    return graph


def add_tweet_edges(graph, tweets):
    count = 0
    for tweet_i in tweets:
        for tweet_j in tweets:
            similarity = cosine_similarity(tweet_i["text"], tweet_j["text"])
            graph.add_edge(tweet_i["id_str"], tweet_j["id_str"], weight=similarity)
            print(count)
            count += 1
