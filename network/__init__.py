import os

import scipy.sparse

import common.mongo
import common.utils
import common.settings

tweets = common.mongo.get_tweets()
users = common.mongo.get_users()
docs = common.mongo.get_docs()
annotations = common.mongo.get_annotations()

os.makedirs("data/sim/", exist_ok=True)

try:
    print("computing tweets similarity matrix")
    t2t_similarity_matrix = scipy.sparse.load_npz("data/sim/t2t.npz")
except IOError:
    t2t_similarity_matrix = common.utils.compute_similarity_matrix(
        [tweet["text"] for tweet in tweets],
        common.settings.network.getstring("TweetTweetSimilarityMeasure"))
    scipy.sparse.save_npz("data/sim/t2t.npz", t2t_similarity_matrix)

try:
    print("computing docs similarity matrix")
    d2d_similarity_matrix = scipy.sparse.load_npz("data/sim/d2d.npz")
except IOError:
    d2d_similarity_matrix = common.utils.compute_similarity_matrix(
        [doc["text"] for doc in docs],
        common.settings.network.getstring("DocDocSimilarityMeasure"))
    scipy.sparse.save_npz("data/sim/d2d.npz", d2d_similarity_matrix)

try:
    print("computing tweets docs similarity matrix")
    t2t_similarity_matrix = scipy.sparse.load_npz("data/sim/t2d.npz")
except IOError:
    t2d_similarity_matrix = common.utils.compute_similarity_matrix2(
        [tweet["text"] for tweet in tweets], [doc["text"] for doc in docs],
        common.settings.network.getstring("DocTweetSimilarityMeasure"))
    scipy.sparse.save_npz("data/sim/t2d.npz", t2d_similarity_matrix)
