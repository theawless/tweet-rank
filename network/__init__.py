import common.mongo
import common.utils

tweets = common.mongo.get_tweets()
users = common.mongo.get_users()
docs = common.mongo.get_docs()

print("compute tweets similarity matrix")
tweets_similarity_matrix = common.utils.compute_similarity_matrix(tweet["text"] for tweet in tweets)
print("compute docs similarity matrix")
docs_similarity_matrix = common.utils.compute_similarity_matrix(doc["text"] for doc in docs)
