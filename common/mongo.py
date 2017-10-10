from pymongo import MongoClient, ASCENDING

client = MongoClient('localhost', 27017)
vegas_db = client.vegas

tweets_collection = vegas_db.tweets

users_collection = vegas_db.users

docs_collection = vegas_db.docs

annotations_collection = vegas_db.annotations

urls_collection = vegas_db.urls


def get_tweets(sort=True, limit=0):
    if sort:
        tweets_cursor = tweets_collection.find(limit=limit, sort=[("timestamp_ms", ASCENDING)])
    else:
        tweets_cursor = tweets_collection.find(limit=limit)
    return list(tweets_cursor)


def get_users(limit=0):
    users_cursor = users_collection.find(limit=limit)
    return list(users_cursor)


def get_docs(limit=0):
    docs_cursor = docs_collection.find(limit=limit)
    return list(docs_cursor)


def get_annotations(limit=0):
    annotations_cursor = annotations_collection.find(limit=limit)
    return list(annotations_cursor)


def get_urls(limit=0):
    urls_cursor = urls_collection.find(limit=limit)
    return list(urls_cursor)
