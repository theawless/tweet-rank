import pymongo
from pymongo import MongoClient

from docs import filter_docs, hydrate_docs
from tweets import filter_tweets

client = MongoClient('localhost', 27017)
vegas_db = client.vegas
tweets_collection = vegas_db.tweets
users_collection = vegas_db.users
docs_collection = vegas_db.docs


def get_tweets():
    tweets_cursor = tweets_collection.find().sort("timestamp_ms", pymongo.ASCENDING)
    return list(tweets_cursor)


def get_users():
    users_cursor = users_collection.find()
    return list(users_cursor)


def get_docs():
    docs_cursor = docs_collection.find()
    return list(docs_cursor)


def _save_tweets_from_tweets(tweets):
    tweets_collection.delete_many({})
    tweets_dict = {}
    for tweet in tweets:
        if "limit" in tweet:
            continue

        if tweet["id_str"] not in tweets_dict:
            tweets_dict[tweet["id_str"]] = tweet

        # retweet
        if "retweeted_status" in tweet:
            if tweet["retweeted_status"]["id_str"] not in tweets_dict:
                tweets_dict[tweet["retweeted_status"]["id_str"]] = tweet["retweeted_status"]
    filtered_tweets = filter_tweets(tweets_dict.values())
    tweets_collection.insert_many(filtered_tweets)


def _save_users_from_tweets(tweets):
    users_dict = {}
    for tweet in tweets:
        # author
        user = tweet["user"]
        users_dict[user["id_str"]] = user

        # retweet
        if "retweeted_status" in tweet:
            user = tweet["retweeted_status"]["user"]
            users_dict[user["id_str"]] = user

        # reply
        in_reply_to_user_id_str = tweet["in_reply_to_user_id_str"]
        if in_reply_to_user_id_str is not None:
            if in_reply_to_user_id_str not in users_dict:
                users_dict[in_reply_to_user_id_str] = {"id_str": in_reply_to_user_id_str}

        # mentions
        for mention in tweet["entities"]["user_mentions"]:
            if mention["id_str"] not in users_dict:
                users_dict[mention["id_str"]] = {"id_str": mention["id_str"]}
    users_collection.insert_many(users_dict.values())


def _save_docs_from_tweets(tweets):
    docs_dict = {}
    for tweet in tweets:
        for doc in tweet["entities"]["urls"]:
            id_str = doc["url"]
            if id_str not in docs_dict:
                doc["id_str"] = id_str
                doc["tweet_id"] = tweet["id"]
                doc["tweet_text"] = tweet["text"]
                docs_dict[id_str] = doc

        # retweet
        if "retweeted_status" in tweet:
            for doc in tweet["retweeted_status"]["entities"]["urls"]:
                id_str = doc["url"]
                if id_str not in docs_dict:
                    doc["id_str"] = id_str
                    doc["tweet_id"] = tweet["retweeted_status"]["id"]
                    doc["tweet_text"] = tweet["retweeted_status"]["text"]
                    docs_dict[id_str] = doc
    filtered_docs = filter_docs(docs_dict.values())
    hydrate_docs(filtered_docs)
    docs_collection.insert_many(filtered_docs)


if __name__ == '__main__':
    _save_tweets_from_tweets(get_tweets())
    _save_users_from_tweets(get_tweets())
    _save_docs_from_tweets(get_tweets())
