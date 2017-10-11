from networkx import union, DiGraph

from analyse.network import add_tweet_vertices, add_user_vertices, add_doc_vertices
from analyse.network import add_user_tweet_edges, add_doc_tweet_edges
from analyse.network import add_user_user_edges, add_tweet_tweet_edges
from analyse.utils import compute_pagerank, compute_trihits


def make_graphs():
    t2t_graph = DiGraph()
    add_tweet_vertices(t2t_graph)

    u2u_graph = DiGraph()
    add_user_vertices(u2u_graph)

    d2d_graph = DiGraph()
    add_doc_vertices(d2d_graph)
    return t2t_graph, u2u_graph, d2d_graph


def homo(t2t_graph, u2u_graph, d2d_graph):
    add_tweet_tweet_edges(t2t_graph, 0.0)
    compute_pagerank(t2t_graph)

    add_user_user_edges(u2u_graph)
    compute_pagerank(u2u_graph)

    # add_doc_doc_edges(d2d_graph, 0.0)
    compute_pagerank(d2d_graph)


def hetero(graph):
    add_user_tweet_edges(graph, 0.0)
    add_doc_tweet_edges(graph)

    L = {'ut': 0.1, 'tu': 0.1, 'dt': 0.1, 'td': 0.1}
    compute_trihits(graph, L=L)


def main():
    t2t_graph, u2u_graph, d2d_graph = make_graphs()
    homo(t2t_graph, u2u_graph, d2d_graph)
    graph = union(union(t2t_graph, u2u_graph), d2d_graph)
    hetero(graph)

    # do stuff
    print(graph)


if __name__ == '__main__':
    main()
