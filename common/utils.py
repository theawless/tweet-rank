import os
import re
import string

import networkx
import nltk
import numpy
import scipy.sparse
import sklearn.feature_extraction.text


def compute_similarity_matrix(items):
    vectorizer = sklearn.feature_extraction.text.TfidfVectorizer(tokenizer=tokenize_text,
                                                                 stop_words='english')
    tfidf = vectorizer.fit_transform(items)
    similarity_matrix = tfidf * tfidf.T
    return scipy.sparse.csr_matrix(similarity_matrix)


def compute_dcg(scores):
    i, dcg = 1, 0.0
    for score in scores:
        dcg += (numpy.math.pow(2, score) - 1) / numpy.math.log(i + 1, 2)
        i += 1
    return dcg


def tokenize_text(text):
    text = re.sub(r"http\S+", "", text)
    text = text.translate(string.punctuation)
    words = nltk.word_tokenize(text)
    words = [re.sub("[^A-Za-z0-9]", "", word) for word in words]
    return words


os.makedirs("data/pickle/", exist_ok=True)


def save_graph(graph, name):
    print("saving graph", name)
    networkx.write_gpickle(graph, "data/pickle/" + name + ".pickle")


def read_graph(name):
    print("reading graph", name)
    return networkx.read_gpickle("data/pickle/" + name + ".pickle")
