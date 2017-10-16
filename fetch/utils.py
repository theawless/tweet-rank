from common.settings import clean_settings
from common.utils import tokenize_text


def filter_tweets(tweets):
    print("filtering tweets")
    filtered_tweets = []
    for tweet in tweets:
        if tweet["text"] == "RT":
            tweet["text"] = tweets["text"][2:]
        if tokenize_text(tweet["text"]):
            filtered_tweets.append(tweet)
    return filtered_tweets


def filter_urls(urls):
    print("filtering urls")
    filtered_urls = []
    for url in urls:
        if "twitter.com" not in url["expanded_url"]:
            filtered_urls.append(url)
    return filtered_urls


def clean_tweet(tweet):
    for key in tweet.copy().keys():
        if key not in clean_settings.getstringlist("TweetKeysToSave"):
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


def clean_user(user):
    for key in user.copy().keys():
        if key not in clean_settings.getstringlist("TweetUserKeysToSave"):
            user.pop(key, None)


def _clean_entities(entities):
    for key in entities.copy().keys():
        if key not in clean_settings.getstringlist("TweetEntitiesKeysToSave"):
            entities.pop(key, None)


def clean_url(url):
    for key in url.copy().keys():
        if key not in clean_settings.getstringlist("TweetUrlKeysToSave"):
            url.pop(key, None)


def _clean_user_mention(user_mention):
    for key in user_mention.copy().keys():
        if key not in clean_settings.getstringlist("TweetUserMentionKeysToSave"):
            user_mention.pop(key, None)
