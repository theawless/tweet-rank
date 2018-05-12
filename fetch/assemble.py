from tqdm import tqdm

import common.mongo
import common.settings
import common.tweets
import fetch.utils


def _save_tweets_from_full_tweets(tweets):
    print("saving tweets from full tweets")
    common.mongo.tweets_collection.drop()
    tweets_dict = {}
    for tweet in tqdm(tweets):
        if "limit" in tweet:
            continue

        if tweet["id_str"] not in tweets_dict:
            # fetch.utils.clean_tweet(tweet)
            if "timestamp_ms" not in tweet:
                tweet["timestamp_ms"] = str(common.tweets.time_to_timestamp(tweet["created_at"]))
            if "full_text" in tweet:
                tweet["text"] = tweet["full_text"]
            if "text" in tweet and "coordinates" in tweet:
                tweets_dict[tweet["id_str"]] = tweet

        # retweet
        if "retweeted_status" in tweet:
            retweet = tweet["retweeted_status"]
            if retweet["id_str"] not in tweets_dict:
                if "timestamp_ms" not in retweet:
                    retweet["timestamp_ms"] = str(common.tweets.time_to_timestamp(retweet["created_at"]))
                # fetch.utils.clean_tweet(retweet)
                if "full_text" in retweet:
                    retweet["text"] = retweet["full_text"]
                if "text" in retweet and "coordinates" in retweet and retweet["coordinates"] != "":
                    tweets_dict[retweet["id_str"]] = retweet

    tweets_sorted_with_timestamp = sorted(list(tweets_dict.values()), key=lambda e: e["timestamp_ms"])
    sampled_tweets_chunks = common.tweets.chunk_by_time(tweets_sorted_with_timestamp,
                                                        common.settings.clean.getint("TweetBinning"),
                                                        common.settings.clean.getfloat("TweetSampling"))
    sampled_tweets = []
    for i in range(len(sampled_tweets_chunks)):
        for tweet in sampled_tweets_chunks[i]:
            tweet["hour"] = i
            sampled_tweets.append(tweet)
    filtered_tweets = fetch.utils.filter_tweets(sampled_tweets)
    common.mongo.tweets_collection.insert_many(filtered_tweets)


def _save_users_from_tweets(tweets):
    print("saving users from tweets")
    common.mongo.users_collection.drop()
    users_dict = {}
    for tweet in tqdm(tweets):
        # author
        user = tweet["user"]
        # fetch.utils.clean_user(user)
        users_dict[user["id_str"]] = user

        # retweet
        if "retweeted_status" in tweet:
            user = tweet["retweeted_status"]["user"]
            # fetch.utils.clean_user(user)
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
    common.mongo.users_collection.insert_many(users_dict.values())


def _save_urls_from_tweets(tweets):
    print("saving urls from tweets")
    common.mongo.urls_collection.drop()
    urls_dict = {}
    for tweet in tqdm(tweets):
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
    filtered_urls = fetch.utils.filter_urls(urls_dict.values())
    common.mongo.urls_collection.insert_many(filtered_urls)


def assemble():
    print("assembling")
    _save_tweets_from_full_tweets(common.mongo.get_full_tweets(limit=1000))
    _save_users_from_tweets(common.mongo.get_tweets(False))
    # _save_urls_from_tweets(common.mongo.get_tweets(False))


if __name__ == '__main__':
    assemble()
