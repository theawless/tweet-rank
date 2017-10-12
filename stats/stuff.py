from sys import argv

from nltk import FreqDist
from nltk.corpus import stopwords

from analyse import tweets
from common.utils import tokenize_text


def remove_stop_words(terms):
    return [term for term in terms if term not in stopwords.words('english')]


def find_top_terms(terms, number):
    distribution = FreqDist(terms)
    return distribution.most_common(number)


def find_top_terms_in_tweets():
    vocab = [term for tweet in tweets for term in tokenize_text(tweet["text"].lower())]
    print(find_top_terms(remove_stop_words(vocab), 50))


if __name__ == '__main__':
    if argv[1] == "tweet_top_terms":
        find_top_terms_in_tweets()
