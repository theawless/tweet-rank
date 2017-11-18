import os

import networkx

import common.settings
import common.utils
import network.connect
import network.connect
import network.connect
import network.utils

tt_ts = common.settings.network.getfloatlist("TweetTweetThreshold")
tst_fs = common.settings.network.getfloatlist("TweetSimilarityTweetFactor")
tgt_fs = common.settings.network.getfloatlist("GeoSignalRadius")
dd_ts = common.settings.network.getfloatlist("DocDocThreshold")
tu_ts = common.settings.network.getfloatlist("TweetUserThreshold")
dt_ts = common.settings.network.getfloatlist("DocTweetThreshold")
tdtc_fs = common.settings.network.getfloatlist("TweetDocTweetCommonFactor")
ut_ls = common.settings.network.getfloatlist("LambdaUserTweet")
tu_ls = common.settings.network.getfloatlist("LambdaTweetUser")
dt_ls = common.settings.network.getfloatlist("LambdaDocTweet")
td_ls = common.settings.network.getfloatlist("LambdaTweetDoc")


def make_settings(i):
    def i_or_last(l):
        return l[i] if len(l) > i else l[-1]

    ts = {"tt": i_or_last(tt_ts),
          "dd": i_or_last(dd_ts),
          "tu": i_or_last(tu_ts),
          "dt": i_or_last(dt_ts)}
    fs = {"tst": i_or_last(tst_fs),
          "tgt": i_or_last(tgt_fs),
          "tdtc": i_or_last(tdtc_fs)}
    ls = {"ut": i_or_last(ut_ls),
          "tu": i_or_last(tu_ls),
          "dt": i_or_last(dt_ls),
          "td": i_or_last(td_ls)}
    return ts, fs, ls


def make_graphs():
    t2t_graph = networkx.DiGraph()
    network.connect.add_tweet_vertices(t2t_graph)

    u2u_graph = networkx.DiGraph()
    network.connect.add_user_vertices(u2u_graph)

    d2d_graph = networkx.DiGraph()
    network.connect.add_doc_vertices(d2d_graph)
    return t2t_graph, u2u_graph, d2d_graph


def homo(t2t_graph, u2u_graph, d2d_graph, ts, fs):
    network.connect.add_tweet_tweet_edges(t2t_graph, ts["tt"], fs["tst"])
    network.connect.add_tweet_tweet_geo_signals(t2t_graph, fs["tgt"], ts["tst"], ts["tdtc"])
    network.connect.add_tweet_doc_tweet_common_edges(t2t_graph, d2d_graph, ts["dt"], fs["tdtc"])
    print("computing t2t graph pagerank")
    network.utils.compute_pagerank(t2t_graph)

    network.connect.add_user_user_edges(u2u_graph)
    print("computing u2u graph pagerank")
    network.utils.compute_pagerank(u2u_graph)

    network.connect.add_doc_doc_edges(d2d_graph, ts["dd"])
    print("computing t2t graph pagerank")
    network.utils.compute_pagerank(d2d_graph)


def hetero(graph, ts, ls):
    network.connect.add_doc_tweet_edges(graph, ts["dt"])
    network.connect.add_tweet_user_edges(graph, ts["tu"])
    network.utils.compute_trihits(graph, ls)


def main():
    for i in range(common.settings.network.getint("Iterations")):
        ts, fs, ls = make_settings(i)

        print("making individual graphs")
        t2t_graph, u2u_graph, d2d_graph = make_graphs()
        homo(t2t_graph, u2u_graph, d2d_graph, ts, fs)

        print("merging individual graphs")
        graph = networkx.union(networkx.union(t2t_graph, u2u_graph), d2d_graph)
        hetero(graph, ts, ls)

        common.utils.save_graph(graph, "tweet-user-doc graph", i)
        write_results(graph, i)


def write_results(graph, iteration):
    os.makedirs("data/output/", exist_ok=True)
    with open("data/output/" + str(iteration), "w+") as file:
        lines = []
        for text, score in network.utils.compute_tweet_results(graph):
            lines.append("tweet-score: " + format(score, '.32f') + " tweet-text: " + text + "\n")
        lines.append("\n")
        file.writelines(lines)
    with open("data/output/all", "a+") as file:
        lines = ["iteration no: " + str(iteration) + "\n"]
        for tag, gain in network.utils.compute_ndcg_at_k(graph, 10):
            lines.append("ndcg-score: " + format(gain, '.32f') + " tag: " + tag + "\n")
        lines.append("\n")
        file.writelines(lines)


if __name__ == '__main__':
    main()
