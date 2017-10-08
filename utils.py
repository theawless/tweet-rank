import re
import string

import scipy.sparse
from networkx import pagerank
from nltk import PorterStemmer, word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer


def compute_pagerank(graph):
    ranks = pagerank(graph, weight="weight")
    for node_id in ranks.keys():
        graph.nodes[node_id]["score"] = ranks[node_id]


stemmer = PorterStemmer()


def tokenize_text(text):
    # remove urls
    text = re.sub(r"http\S+", "", text)

    # remove the punctuation
    text = text.translate(string.punctuation)

    # find word stems
    words = word_tokenize(text)
    return [stemmer.stem(item) for item in words]


def compute_similarity_matrix(items):
    vectorizer = TfidfVectorizer(tokenizer=tokenize_text, stop_words='english')
    tfidf = vectorizer.fit_transform(items)
    sim_matrix = tfidf * tfidf.T

    # return coo_matrix for fast iterations
    return scipy.sparse.coo_matrix(sim_matrix)
