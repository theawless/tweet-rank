import networkx

import common.settings
import common.utils
import network.connect
import network.connect
import network.connect
import network.utils


def make_graphs():
    t2t_graph = networkx.DiGraph()
    network.connect.add_tweet_vertices(t2t_graph)

    u2u_graph = networkx.DiGraph()
    network.connect.add_user_vertices(u2u_graph)

    d2d_graph = networkx.DiGraph()
    network.connect.add_doc_vertices(d2d_graph)
    return t2t_graph, u2u_graph, d2d_graph


def homo(t2t_graph, u2u_graph, d2d_graph):
    network.connect.add_tweet_tweet_edges(t2t_graph, common.settings.network.getfloat("TweetTweetThreshold"))
    print("computing t2t graph pagerank")
    network.utils.compute_pagerank(t2t_graph)
    common.utils.save_graph(t2t_graph, "tweets-text-rank")

    network.connect.add_user_user_edges(u2u_graph)
    print("computing u2u graph pagerank")
    network.utils.compute_pagerank(u2u_graph)
    common.utils.save_graph(u2u_graph, "users-text-rank")

    network.connect.add_doc_doc_edges(d2d_graph, common.settings.network.getfloat("DocDocThreshold"))
    print("computing t2t graph pagerank")
    network.utils.compute_pagerank(d2d_graph)
    common.utils.save_graph(d2d_graph, "docs-text-rank")


def hetero(graph):
    network.connect.add_tweet_user_edges(graph, common.settings.network.getfloat("TweetUserThreshold"))
    common.utils.save_graph(graph, "full-user-tweet-links")

    network.connect.add_doc_tweet_edges(graph, common.settings.network.getfloat("DocTweetThreshold"))
    common.utils.save_graph(graph, "full-doc-tweet-links")

    network.utils.compute_trihits(graph, {'ut': common.settings.network.getfloat("LambdaUserTweet"),
                                          'tu': common.settings.network.getfloat("LambdaTweetUser"),
                                          'dt': common.settings.network.getfloat("LambdaDocTweet"),
                                          'td': common.settings.network.getfloat("LambdaTweetDoc")})
    common.utils.save_graph(graph, "full-trihits")


def main():
    print("making individual graphs")
    t2t_graph, u2u_graph, d2d_graph = make_graphs()
    homo(t2t_graph, u2u_graph, d2d_graph)

    print("merging individual graphs")
    graph = networkx.union(networkx.union(t2t_graph, u2u_graph), d2d_graph)
    hetero(graph)
    show_results(graph)


def show_results(graph):
    for text, score in network.utils.compute_tweet_results(graph):
        print(text, format(score, '.32f'))
    for tag, gain in network.utils.compute_ndcg_at_k(graph, 10):
        print(tag, format(gain, '.32f'))


if __name__ == '__main__':
    main()
