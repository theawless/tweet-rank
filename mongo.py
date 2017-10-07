import pymongo
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
vegas_db = client.vegas
tweets_collection = vegas_db.tweets
users_collection = vegas_db.users


def get_tweets():
    tweets_cursor = tweets_collection.find().sort("timestamp_ms", pymongo.ASCENDING)
    tweets = list(tweets_cursor)
    return tweets


def save_users_from_tweets(tweets):
    users = {}
    for tweet in tweets:
        # author
        user = tweet["user"]
        users[user["id_str"]] = user

        # retweet
        if "retweeted_status" in tweet:
            user = tweet["retweeted_status"]["user"]
            users[user["id_str"]] = user

        # reply
        in_reply_to_user_id_str = tweet["in_reply_to_user_id_str"]
        if in_reply_to_user_id_str is not None:
            if in_reply_to_user_id_str not in users:
                users[in_reply_to_user_id_str] = {"id_str": in_reply_to_user_id_str}

        # mentions
        for mention in tweet["entities"]["user_mentions"]:
            if mention["id_str"] not in users:
                users[mention["id_str"]] = {"id_str": mention["id_str"]}
    users_collection.insert_many(users.values())


def clean_tweets():
    tweets_collection.delete_many({"limit": {"$exists": "true"}})
    tweets = get_tweets()
    cleaned_tweets = {}
    for tweet in tweets:
        if not tweet["id_str"] in cleaned_tweets:
            cleaned_tweets[tweet["id_str"]] = tweet

        # retweet
        if "retweeted_status" in tweet:
            if not tweet["retweeted_status"]["id_str"] in cleaned_tweets:
                cleaned_tweets[tweet["retweeted_status"]["id_str"]] = tweet["retweeted_status"]
    tweets_collection.delete_many({})
    tweets_collection.insert_many(cleaned_tweets.values())


def get_users():
    users_cursor = users_collection.find()
    users = list(users_cursor)
    return users


if __name__ == '__main__':
    clean_tweets()
    save_users_from_tweets(get_tweets())
