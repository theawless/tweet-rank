from pymongo import MongoClient, ASCENDING

from common.settings import mongo_settings

settings = mongo_settings

client = MongoClient(settings.getstring("Host"), settings.getint("Port"))
database = client[settings.getstring("Database")]

full_tweets_collection = database[settings.getstring("FullTweetsCollection")]
tweets_collection = database[settings.getstring("TweetsCollection")]
users_collection = database[settings.getstring("UsersCollection")]
docs_collection = database[settings.getstring("DocsCollection")]
annotations_collection = database[settings.getstring("AnnotationsCollection")]
urls_collection = database[settings.getstring("UrlsCollection")]


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
