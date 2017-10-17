import pymongo

import common.settings

client = pymongo.MongoClient(host=common.settings.mongo.getstring("Host"),
                             port=common.settings.mongo.getint("Port"),
                             username=common.settings.mongo.getstring("Username") or None,
                             password=common.settings.mongo.getstring("Password") or None)
database = client[common.settings.mongo.getstring("Database")]

full_tweets_collection = database[common.settings.mongo.getstring("FullTweetsCollection")]
tweets_collection = database[common.settings.mongo.getstring("TweetsCollection")]
users_collection = database[common.settings.mongo.getstring("UsersCollection")]
docs_collection = database[common.settings.mongo.getstring("DocsCollection")]
annotations_collection = database[common.settings.mongo.getstring("AnnotationsCollection")]
urls_collection = database[common.settings.mongo.getstring("UrlsCollection")]


def get_full_tweets(limit=0):
    print("getting full tweets")
    return full_tweets_collection.find(limit=limit)


def get_tweets(sort=True, hour=-1, limit=0):
    print("getting tweets")
    sort_list = [("timestamp_ms", pymongo.ASCENDING)] if sort else []
    find_dict = {"hour": hour} if hour != -1 else {}
    tweets_cursor = tweets_collection.find(find_dict, limit=limit, sort=sort_list)
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
