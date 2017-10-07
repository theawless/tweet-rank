from networkx import DiGraph, pagerank

from utils import compute_tweet_sim_matrix

T_tt = 0.0

def init_tweet_graph(tweets):
    t2t_graph = DiGraph()
    add_vertices(t2t_graph, tweets, "tweet")
    add_tweet_edges(t2t_graph, tweets)
    ranks = pagerank(t2t_graph, weight="weight")
    for tweet_id in ranks.keys():
        t2t_graph.nodes[tweet_id]["score"] = ranks[tweet_id]
    return t2t_graph


def init_user_graph(tweets, users):
    u2u_graph = DiGraph()
    add_vertices(u2u_graph, users, "user")
    add_user_edges(u2u_graph, tweets)
    ranks = pagerank(u2u_graph, weight="weight")
    for user_id in ranks.keys():
        u2u_graph.nodes[user_id]["score"] = ranks[user_id]
    return u2u_graph


def init_web_graph():
    pass


def add_vertices(graph, items, genre):
    for item in items:
        graph.add_node(item["id_str"], content=item, genre=genre, score=0)


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
            if not graph.has_edge(user_i, user_j):
                graph.add_edge(user_i, user_j, weight=0)
            graph[user_i][user_j]["weight"] += 1
    return graph


def add_tweet_edges(graph, tweets):
    similarity_matrix = compute_tweet_sim_matrix([tweet['text'] for tweet in tweets])
    for i,j,v in zip(similarity_matrix.row, similarity_matrix.col, similarity_matrix.data):
        if i < j and v > T_tt:
            graph.add_edge(tweets[i]["id_str"], tweets[j]["id_str"], weight=v)
            graph.add_edge(tweets[j]["id_str"], tweets[i]["id_str"], weight=v)
