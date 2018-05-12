import os
import re
import string

import gensim
import networkx
import nltk
import nltk.corpus
import numpy
import scipy.sparse
import sklearn.feature_extraction.text
from tqdm import tqdm

import common.neo4j
import common.settings

if (common.settings.network.getstring("TweetTweetSimilarityMeasure") == "word2vec" or
            common.settings.network.getstring("DocDocSimilarityMeasure") == "word2vec" or
            common.settings.network.getstring("DocTweetSimilarityMeasure") == "word2vec"):
    print('Loading Word2Vec Embeddings')
    word2vec_model = gensim.models.KeyedVectors.load_word2vec_format('data/GoogleNews-vectors-negative300.bin.gz',
                                                                     binary=True,
                                                                     limit=500000)


def compute_similarity_matrix(items, measure):
    if measure == "tfidf":
        print("computing tfidf similarities")
        vectorizer = sklearn.feature_extraction.text.TfidfVectorizer(tokenizer=tokenize_text)
        tfidf = vectorizer.fit_transform(items)
        similarity_matrix = tfidf * tfidf.T
        return scipy.sparse.csr_matrix(similarity_matrix)
    elif measure == "word2vec":
        return compute_word2vec_similarity_matrix(items, items)


def compute_similarity_matrix2(items1, items2, measure):
    if measure == "tfidf":
        print("computing tfidf similarities")
        tfidf_transformer = sklearn.feature_extraction.text.TfidfTransformer()
        vectorizer = sklearn.feature_extraction.text.CountVectorizer(tokenizer=tokenize_text)
        items1_matrix = vectorizer.fit_transform(items1)
        tfidf_transformer.fit(items1_matrix)
        tfidf_transformer.transform(items1_matrix)

        similarity_matrix = []
        for item2 in items2:
            item2_vector = vectorizer.transform([item2])
            tfidf_transformer.fit(item2_vector)
            tfidf_item2 = tfidf_transformer.transform(item2_vector)
            result = numpy.array([numpy.asscalar(s) for s in sklearn.metrics.pairwise.cosine_similarity(items1_matrix,
                                                                                                        tfidf_item2)])
            similarity_matrix.append(result)
        return scipy.sparse.csr_matrix(similarity_matrix)
    elif measure == "word2vec":
        return compute_word2vec_similarity_matrix(items1, items2)


def compute_word2vec_similarity_matrix(items1, items2):
    similarity_matrix = numpy.zeros((len(items1), len(items2)))
    print("computing word2vec similarities")
    for i in tqdm(range(len(items1))):
        for j in range(i + 1):
            tokens1 = tokenize_text_word2vec(items1[i])
            tokens2 = tokenize_text_word2vec(items2[j])
            if tokens1 and tokens2:
                similarity = word2vec_model.n_similarity(tokens1, tokens2)
                similarity_matrix[i, j] = similarity
                similarity_matrix[j, i] = similarity
    return scipy.sparse.csr_matrix(similarity_matrix)


def compute_dcg(scores):
    i, dcg = 1, 0.0
    for score in scores:
        dcg += (numpy.math.pow(2, score) - 1) / numpy.math.log(i + 1, 2)
        i += 1
    return dcg


def tokenize_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = text.translate(string.punctuation)
    words = nltk.word_tokenize(text)
    words = [re.sub("[^A-Za-z0-9]", "", word) for word in words]

    final_words = []
    for word in words:
        if not word:
            continue
        if word in nltk.corpus.stopwords.words("english"):
            continue
        if word.startswith("@") or word.startswith("#"):
            continue
        if word.isnumeric():
            continue
        final_words.append(word)
    return final_words


def tokenize_text_word2vec(text):
    words = tokenize_text(text)
    final_words = []
    for word in words:
        if word in word2vec_model:
            final_words.append(word)
    return final_words


def save_graph(graph, name, iteration):
    print("saving graph", name)
    if common.settings.network.getboolean("PickleSaveGraph"):
        os.makedirs("data/pickle/", exist_ok=True)
        networkx.write_gpickle(graph, "data/pickle/" + str(iteration) + "_" + name + ".pickle")
    if common.settings.network.getint("CreateNeo4jGraphAtIteration") == iteration:
        common.neo4j.write_neo(graph.nodes(data=True), graph.edges(data=True))


def read_graph(name):
    print("reading graph", name)
    return networkx.read_gpickle("data/pickle/" + name + ".pickle")
