from igraph import plot

from homo import init_tweet_graph, init_user_graph
from mongo import get_tweets, get_users
from utils import filter_tweets

tweets = filter_tweets(get_tweets())
users = get_users()


def init_graph():
    t2t_graph = init_tweet_graph(tweets)
    u2u_graph = init_user_graph(tweets, users)

    layout = t2t_graph.layout_lgl()
    plot(t2t_graph, layout=layout)
    layout = u2u_graph.layout_lgl()
    plot(u2u_graph, layout=layout)


def main():
    init_graph()


if __name__ == '__main__':
    main()
