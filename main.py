from networkx import union, DiGraph

from mongo import get_tweets, get_users, get_docs
from network import add_tweet_user_edges, add_doc_tweet_edges
from network import add_user_user_edges, add_doc_doc_edges, add_tweet_tweet_edges
from network import add_vertices
from utils import compute_pagerank

tweets = get_tweets()
users = get_users()
docs = get_docs()


def make_graphs():
    t2t_graph = DiGraph()
    add_vertices(t2t_graph, tweets, "tweet")

    u2u_graph = DiGraph()
    add_vertices(u2u_graph, users, "user")

    d2d_graph = DiGraph()
    add_vertices(d2d_graph, docs, "doc")
    return t2t_graph, u2u_graph, d2d_graph


def homo(t2t_graph, u2u_graph, d2d_graph):
    add_tweet_tweet_edges(t2t_graph, tweets, 0.0)
    compute_pagerank(t2t_graph)

    add_user_user_edges(u2u_graph, tweets)
    compute_pagerank(u2u_graph)

    add_doc_doc_edges(d2d_graph, docs, 0.0)
    compute_pagerank(d2d_graph)


def hetero(graph):
    add_tweet_user_edges(graph, tweets, 0.0)
    add_doc_tweet_edges(graph, tweets, docs)


def main():
    t2t_graph, u2u_graph, d2d_graph = make_graphs()
    homo(t2t_graph, u2u_graph, d2d_graph)
    graph = union(union(t2t_graph, u2u_graph), d2d_graph)
    hetero(graph)

    # do stuff
    print(graph)


if __name__ == '__main__':
    main()
