import os

import scipy.sparse

import common.mongo
import common.utils
import common.settings

tweets = common.mongo.get_tweets(limit=1000)
users = common.mongo.get_users()
docs = common.mongo.get_docs()
annotations = common.mongo.get_annotations()

os.makedirs("data/sim/", exist_ok=True)

t2t_sim = common.settings.network.getstring("TweetTweetSimilarityMeasure")
try:
    print("computing tweets similarity matrix")
    t2t_similarity_matrix = scipy.sparse.load_npz("data/sim/t2t" + t2t_sim + ".npz")
except IOError:
    t2t_similarity_matrix = common.utils.compute_similarity_matrix(
        [tweet["text"] for tweet in tweets], t2t_sim)
    scipy.sparse.save_npz("data/sim/t2t" + t2t_sim + ".npz", t2t_similarity_matrix)

d2d_sim = common.settings.network.getstring("DocDocSimilarityMeasure")
try:
    print("computing docs similarity matrix")
    d2d_similarity_matrix = scipy.sparse.load_npz("data/sim/d2d" + d2d_sim + ".npz")
except IOError:
    d2d_similarity_matrix = common.utils.compute_similarity_matrix(
        [doc["text"] for doc in docs], d2d_sim)
    scipy.sparse.save_npz("data/sim/d2d" + d2d_sim + ".npz", d2d_similarity_matrix)

t2d_sim = common.settings.network.getstring("DocTweetSimilarityMeasure")
try:
    print("computing tweets docs similarity matrix")
    t2d_similarity_matrix = scipy.sparse.load_npz("data/sim/t2d" + t2d_sim + ".npz")
except IOError:
    t2d_similarity_matrix = common.utils.compute_similarity_matrix2(
        [tweet["text"] for tweet in tweets], [doc["text"] for doc in docs], t2d_sim)
    scipy.sparse.save_npz("data/sim/t2d" + t2d_sim + ".npz", t2d_similarity_matrix)
