from networkx import union, DiGraph

from analyse import tweets
from analyse.network import add_tweet_user_edges, add_doc_tweet_edges
from analyse.network import add_tweet_vertices, add_user_vertices, add_doc_vertices, add_doc_doc_edges
from analyse.network import add_user_user_edges, add_tweet_tweet_edges
from analyse.utils import compute_pagerank, compute_trihits, graph_results
from common.utils import save_graph


def make_graphs():
    t2t_graph = DiGraph()
    add_tweet_vertices(t2t_graph)

    u2u_graph = DiGraph()
    add_user_vertices(u2u_graph)

    d2d_graph = DiGraph()
    add_doc_vertices(d2d_graph)
    return t2t_graph, u2u_graph, d2d_graph


def homo(t2t_graph, u2u_graph, d2d_graph):
    add_tweet_tweet_edges(t2t_graph, 0.5)
    compute_pagerank(t2t_graph)
    save_graph(t2t_graph, "tweets-text-rank")

    add_user_user_edges(u2u_graph)
    compute_pagerank(u2u_graph)
    save_graph(u2u_graph, "users-text-rank")

    add_doc_doc_edges(d2d_graph, 0.5)
    compute_pagerank(d2d_graph)
    save_graph(d2d_graph, "docs-text-rank")


def hetero(graph):
    add_tweet_user_edges(graph, 0.5)
    save_graph(graph, "full-user-tweet-links")

    add_doc_tweet_edges(graph, 0.5)
    save_graph(graph, "full-doc-tweet-links")

    L = {'ut': 0.4, 'tu': 0.2, 'dt': 0.0, 'td': 0.0}
    compute_trihits(graph, L=L)
    save_graph(graph, "full-trihits")


def main():
    t2t_graph, u2u_graph, d2d_graph = make_graphs()
    homo(t2t_graph, u2u_graph, d2d_graph)
    print_results(graph_results(t2t_graph))

    graph = union(union(t2t_graph, u2u_graph), d2d_graph)
    hetero(graph)
    print_results(graph_results(graph))


def print_results(stuff):
    for tweet_node in stuff:
        print(tweets[tweet_node["index"]]["text"], format(tweet_node["score"], '.32f'))


if __name__ == '__main__':
    main()
