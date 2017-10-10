from common.mongo import get_tweets
from common.mongo import tweets_collection, users_collection, urls_collection
from common.utils import tweet_time_to_timestamp, tweets_chunk_by_time
from fetch.utils import filter_tweets, filter_urls, clean_tweet, clean_user


def _save_tweets_from_full_tweets(tweets):
    tweets_collection.drop()
    tweets_dict = {}
    for tweet in tweets:
        if "limit" in tweet:
            continue

        if tweet["id_str"] not in tweets_dict:
            clean_tweet(tweet)
            tweets_dict[tweet["id_str"]] = tweet

        # retweet
        if "retweeted_status" in tweet:
            retweet = tweet["retweeted_status"]
            if retweet["id_str"] not in tweets_dict:
                retweet["timestamp_ms"] = str(tweet_time_to_timestamp(retweet["created_at"]))
                clean_tweet(retweet)
                tweets_dict[retweet["id_str"]] = retweet

    tweets_sorted_with_timestamp = sorted(list(tweets_dict.values()), key=lambda e: e["timestamp_ms"])
    sampled_tweets_chunks = tweets_chunk_by_time(tweets_sorted_with_timestamp, 0.1)
    sampled_tweets = [tweet for sampled_tweets_chunk in sampled_tweets_chunks for tweet in sampled_tweets_chunk]
    filtered_tweets = filter_tweets(sampled_tweets)
    tweets_collection.insert_many(filtered_tweets)


def _save_users_from_tweets(tweets):
    users_collection.drop()
    users_dict = {}
    for tweet in tweets:
        # author
        user = tweet["user"]
        clean_user(user)
        users_dict[user["id_str"]] = user

        # retweet
        if "retweeted_status" in tweet:
            user = tweet["retweeted_status"]["user"]
            clean_user(user)
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


def _save_urls_from_tweets(tweets):
    urls_collection.drop()
    urls_dict = {}
    for tweet in tweets:
        for url in tweet["entities"]["urls"]:
            id_str = url["url"]
            if id_str not in urls_dict:
                url["id_str"] = id_str
                url["tweet_id_str"] = tweet["id_str"]
                url["tweet_text"] = tweet["text"]
                urls_dict[id_str] = url

        # retweet
        if "retweeted_status" in tweet:
            retweet = tweet["retweeted_status"]
            for url in retweet["entities"]["urls"]:
                id_str = url["url"]
                if id_str not in urls_dict:
                    url["id_str"] = id_str
                    url["tweet_id_str"] = retweet["id_str"]
                    url["tweet_text"] = retweet["text"]
                    urls_dict[id_str] = url
    filtered_urls = filter_urls(urls_dict.values())
    urls_collection.insert_many(filtered_urls)


def clean():
    _save_tweets_from_full_tweets(get_tweets(True, False))
    _save_users_from_tweets(get_tweets(False, False))
    _save_urls_from_tweets(get_tweets(False, False))


if __name__ == '__main__':
    clean()