from common.utils import tokenize_text

# not sure if we should add plurals
personal_pronouns = ["i", "me", "mine", "my"]

# taken from https://www.mltcreative.com/blog/social-media-minute-big-a-list-of-twitter-slang-and-definitions/
twitter_slangs = open("data/twitter-slangs.txt").readlines()


def filter_tweets(tweets):
    filtered_tweets = []
    for tweet in tweets:
        if not any(word in tokenize_text(tweet["text"]) for word in personal_pronouns):
            if not any(word in tweet["text"] for word in twitter_slangs):
                filtered_tweets.append(tweet)
    return filtered_tweets


def filter_urls(urls):
    filtered_urls = []
    for url in urls:
        if "twitter.com" not in url["expanded_url"]:
            filtered_urls.append(url)
    return filtered_urls


save_tweet_keys = ["text", "id_str", "in_reply_to_user_id_str", "created_at", "entities", "retweeted_status", "user",
                   "timestamp_ms"]


def clean_tweet(tweet):
    for key in tweet.copy().keys():
        if key not in save_tweet_keys:
            tweet.pop(key, None)

    clean_user(tweet["user"])
    _clean_entities(tweet["entities"])
    for url in tweet["entities"]["urls"]:
        clean_url(url)
    for user_mention in tweet["entities"]["user_mentions"]:
        _clean_user_mention(user_mention)

    # retweet
    if "retweeted_status" in tweet:
        clean_tweet(tweet["retweeted_status"])


save_user_keys = ["id_str"]


def clean_user(user):
    for key in user.copy().keys():
        if key not in save_user_keys:
            user.pop(key, None)


save_entities_keys = ["user_mentions", "urls"]


def _clean_entities(entities):
    for key in entities.copy().keys():
        if key not in save_entities_keys:
            entities.pop(key, None)


save_url_keys = ["expanded_url", "url"]


def clean_url(url):
    for key in url.copy().keys():
        if key not in save_url_keys:
            url.pop(key, None)


save_user_mention_keys = ["id_str"]


def _clean_user_mention(user_mention):
    for key in user_mention.copy().keys():
        if key not in save_user_mention_keys:
            user_mention.pop(key, None)
