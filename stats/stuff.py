import sys

import nltk
import nltk.corpus

import common.mongo
import common.utils


def remove_stop_words(terms):
    return [term for term in terms if term not in nltk.corpus.stopwords.words('english')]


def find_top_terms(terms, number):
    distribution = nltk.FreqDist(terms)
    return distribution.most_common(number)


def find_top_terms_in_tweets():
    vocab = [term for tweet in common.mongo.get_tweets() for term in common.utils.tokenize_text(tweet["text"].lower())]
    print(find_top_terms(remove_stop_words(vocab), 50))


if __name__ == '__main__':
    if sys.argv[1] == "tweet_top_terms":
        find_top_terms_in_tweets()
