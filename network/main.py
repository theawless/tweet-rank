from networkx import union, DiGraph

from common.settings import network_settings
from common.utils import save_graph
from network.network import add_tweet_user_edges, add_doc_tweet_edges
from network.network import add_tweet_vertices, add_user_vertices, add_doc_vertices, add_doc_doc_edges
from network.network import add_user_user_edges, add_tweet_tweet_edges
from network.utils import compute_pagerank, compute_trihits, graph_results

settings = network_settings


def make_graphs():
    t2t_graph = DiGraph()
    add_tweet_vertices(t2t_graph)

    u2u_graph = DiGraph()
    add_user_vertices(u2u_graph)

    d2d_graph = DiGraph()
    add_doc_vertices(d2d_graph)
    return t2t_graph, u2u_graph, d2d_graph


def homo(t2t_graph, u2u_graph, d2d_graph):
    add_tweet_tweet_edges(t2t_graph, settings.getfloat("TweetTweetThreshold"))
    print("computing t2t graph pagerank")
    compute_pagerank(t2t_graph)
    save_graph(t2t_graph, "tweets-text-rank")

    add_user_user_edges(u2u_graph)
    print("computing u2u graph pagerank")
    compute_pagerank(u2u_graph)
    save_graph(u2u_graph, "users-text-rank")

    add_doc_doc_edges(d2d_graph, settings.getfloat("DocDocThreshold"))
    print("computing t2t graph pagerank")
    compute_pagerank(d2d_graph)
    save_graph(d2d_graph, "docs-text-rank")


def hetero(graph):
    add_tweet_user_edges(graph, settings.getfloat("TweetUserThreshold"))
    save_graph(graph, "full-user-tweet-links")

    add_doc_tweet_edges(graph, settings.getfloat("DocTweetThreshold"))
    save_graph(graph, "full-doc-tweet-links")

    compute_trihits(graph, {'ut': settings.getfloat("LambdaUserTweet"),
                            'tu': settings.getfloat("LambdaTweetUser"),
                            'dt': settings.getfloat("LambdaDocTweet"),
                            'td': settings.getfloat("LambdaTweetDoc")})
    save_graph(graph, "full-trihits")


def main():
    print("making individual graphs")
    t2t_graph, u2u_graph, d2d_graph = make_graphs()
    homo(t2t_graph, u2u_graph, d2d_graph)
    print_results(graph_results(t2t_graph))

    print("merging individual graphs")
    graph = union(union(t2t_graph, u2u_graph), d2d_graph)
    hetero(graph)
    print_results(graph_results(graph))


def print_results(scores):
    print()
    for text, score in scores:
        print(text, format(score, '.32f'))


if __name__ == '__main__':
    main()
