import common.mongo
import common.settings
import common.utils

tweets = common.mongo.get_tweets()
users = common.mongo.get_users()
docs = common.mongo.get_docs()
annotations = common.mongo.get_annotations()

print("computing tweets similarity matrix")
t2t_similarity_matrix = common.utils.compute_similarity_matrix([tweet["text"] for tweet in tweets],
                                                               common.settings.network.getstring("SimilarityMeasure"))
print("computing docs similarity matrix")
d2d_similarity_matrix = common.utils.compute_similarity_matrix([doc["text"] for doc in docs],
                                                               common.settings.network.getstring("SimilarityMeasure"))
print("computing tweets docs similarity matrix")
t2d_similarity_matrix = common.utils.compute_similarity_matrix2([tweet["text"] for tweet in tweets],
                                                                [doc["text"] for doc in docs],
                                                                common.settings.network.getstring("SimilarityMeasure"))
