from common.mongo import get_tweets, get_users, get_docs
from common.utils import compute_similarity_matrix

tweets = get_tweets()
users = get_users()
docs = get_docs()

print("compute tweets similarity matrix")
tweets_similarity_matrix = compute_similarity_matrix(tweet["text"] for tweet in tweets)
print("compute docs similarity matrix")
docs_similarity_matrix = compute_similarity_matrix(doc["text"] for doc in docs)
