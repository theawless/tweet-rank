from sys import argv

from analyse import tweets
from analyse.utils import find_top_terms, remove_stop_words
from common.utils import tokenize_text


def find_top_terms_in_tweets():
    vocab = [term for tweet in tweets for term in tokenize_text(tweet["text"].lower())]
    print(find_top_terms(remove_stop_words(vocab), 50))


if __name__ == '__main__':
    if argv[1] == "tweet_top_terms":
        find_top_terms_in_tweets()
