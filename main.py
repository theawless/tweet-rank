import matplotlib.pyplot as plot
from networkx import union
from networkx.drawing import draw

from homo import init_tweet_graph, init_user_graph
from mongo import get_tweets, get_users
from utils import filter_tweets

tweets = filter_tweets(get_tweets())
users = get_users()


def init_graph():
    t2t_graph = init_tweet_graph(tweets)
    u2u_graph = init_user_graph(tweets, users)
    mix_graph = union(t2t_graph, u2u_graph)

    for v in mix_graph.nodes.data(): print(v)

    return mix_graph


def main():
    graph = init_graph()

    plot.subplot(222)
    draw(graph)
    plot.show()


if __name__ == '__main__':
    main()
