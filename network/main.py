import networkx

import common.settings
import common.utils
import network.connect
import network.connect
import network.connect
import network.utils

tt_ts = common.settings.network.getfloatlist("TweetTweetThreshold")
dd_ts = common.settings.network.getfloatlist("DocDocThreshold")
tu_ts = common.settings.network.getfloatlist("TweetUserThreshold")
dt_ts = common.settings.network.getfloatlist("DocTweetThreshold")
ut_ls = common.settings.network.getfloatlist("LambdaUserTweet")
tu_ls = common.settings.network.getfloatlist("LambdaTweetUser")
dt_ls = common.settings.network.getfloatlist("LambdaDocTweet")
td_ls = common.settings.network.getfloatlist("LambdaTweetDoc")


def make_settings(i):
    ts = {"tt": tt_ts[i] if len(tt_ts) > i else tt_ts[-1],
          "dd": dd_ts[i] if len(dd_ts) > i else dd_ts[-1],
          "tu": tu_ts[i] if len(tu_ts) > i else tu_ts[-1],
          "dt": dt_ts[i] if len(dt_ts) > i else dt_ts[-1]}
    ls = {"ut": ut_ls[i] if len(ut_ls) > i else ut_ls[-1],
          "tu": tu_ls[i] if len(tu_ls) > i else tu_ls[-1],
          "dt": dt_ls[i] if len(dt_ls) > i else dt_ls[-1],
          "td": td_ls[i] if len(td_ls) > i else td_ls[-1]}
    return ts, ls


def make_graphs():
    t2t_graph = networkx.DiGraph()
    network.connect.add_tweet_vertices(t2t_graph)

    u2u_graph = networkx.DiGraph()
    network.connect.add_user_vertices(u2u_graph)

    d2d_graph = networkx.DiGraph()
    network.connect.add_doc_vertices(d2d_graph)
    return t2t_graph, u2u_graph, d2d_graph


def homo(t2t_graph, u2u_graph, d2d_graph, ts):
    network.connect.add_tweet_tweet_edges(t2t_graph, ts["tt"])
    print("computing t2t graph pagerank")
    network.utils.compute_pagerank(t2t_graph)

    network.connect.add_user_user_edges(u2u_graph)
    print("computing u2u graph pagerank")
    network.utils.compute_pagerank(u2u_graph)

    network.connect.add_doc_doc_edges(d2d_graph, ts["dd"])
    print("computing t2t graph pagerank")
    network.utils.compute_pagerank(d2d_graph)


def hetero(graph, ts, ls):
    network.connect.add_tweet_user_edges(graph, ts["tu"])
    network.connect.add_doc_tweet_edges(graph, ts["dt"])
    network.utils.compute_trihits(graph, ls)


def main():
    for i in range(common.settings.network.getint("Iterations")):
        ts, ls = make_settings(i)

        print("making individual graphs")
        t2t_graph, u2u_graph, d2d_graph = make_graphs()
        homo(t2t_graph, u2u_graph, d2d_graph, ts)

        print("merging individual graphs")
        graph = networkx.union(networkx.union(t2t_graph, u2u_graph), d2d_graph)
        hetero(graph, ts, ls)

        common.utils.save_graph(graph, "tweet-user-doc graph", i)
        show_results(graph, i)


def show_results(graph, iteration):
    print("##" * 10, iteration, "##" * 10)
    for text, score in network.utils.compute_tweet_results(graph):
        print("tweet-score:", format(score, '.32f'), "tweet-text:", text)
        print()
    for tag, gain in network.utils.compute_ndcg_at_k(graph, 10):
        print("ndcg-score:", format(gain, '.32f'), "tag:", tag)
        print()


if __name__ == '__main__':
    main()
