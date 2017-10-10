from analyse.utils import compute_similarity_matrix
from common.mongo import get_tweets, get_users, get_docs

tweets = get_tweets()
users = get_users()
docs = get_docs()

tweets_similarity_matrix = compute_similarity_matrix(tweet["id_str"] for tweet in tweets)
docs_similarity_matrix = None  # compute_similarity_matrix(doc["id_str"] for doc in docs)
