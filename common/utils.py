import re
import string

import scipy.sparse
from networkx import write_gpickle, read_gpickle
from nltk import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer


def compute_similarity_matrix(items):
    vectorizer = TfidfVectorizer(tokenizer=tokenize_text, stop_words='english')
    tfidf = vectorizer.fit_transform(items)
    sim_matrix = tfidf * tfidf.T

    # coo_matrix for fast iterations
    return scipy.sparse.csr_matrix(sim_matrix)


def tokenize_text(text):
    # remove urls
    text = re.sub(r"http\S+", "", text)

    # tokenize
    text = text.translate(string.punctuation)
    words = word_tokenize(text)

    # remove weird characters
    words = [re.sub("[^A-Za-z0-9]", "", word) for word in words]

    # remove known words
    words = [word for word in words if word not in [""]]

    return words


def save_graph(graph, name):
    print("saving graph")
    write_gpickle(graph, "data/" + name + ".pickle")


def read_graph(name):
    print("reading graph")
    return read_gpickle("data/" + name + ".pickle")
