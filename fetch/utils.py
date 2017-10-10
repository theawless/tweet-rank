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


def hydrate_docs(docs):
    for doc in docs:
        doc["text"] = "get content using Bing Search / URL"
