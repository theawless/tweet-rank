from pymongo import MongoClient, ASCENDING

client = MongoClient('localhost', 27017)
vegas_db = client.vegas

full_tweets_collection = vegas_db.full_tweets

tweets_collection = vegas_db.tweets

users_collection = vegas_db.users

docs_collection = vegas_db.docs

annotations_collection = vegas_db.annotations

urls_collection = vegas_db.urls


def get_full_tweets(limit=0):
    print("getting full tweets")
    return full_tweets_collection.find(limit=limit)


def get_tweets(sort=True, limit=0):
    print("getting tweets")
    if sort:
        tweets_cursor = tweets_collection.find(limit=limit, sort=[("timestamp_ms", ASCENDING)])
    else:
        tweets_cursor = tweets_collection.find(limit=limit)
    return list(tweets_cursor)


def get_users(limit=0):
    print("getting users")
    users_cursor = users_collection.find(limit=limit)
    return list(users_cursor)


def get_docs(limit=0):
    print("getting docs")
    docs_cursor = docs_collection.find(limit=limit)
    return list(docs_cursor)


def get_annotations(limit=0):
    print("getting annotations")
    annotations_cursor = annotations_collection.find(limit=limit)
    return list(annotations_cursor)


def get_urls(limit=0):
    print("getting urls")
    urls_cursor = urls_collection.find(limit=limit)
    return list(urls_cursor)
