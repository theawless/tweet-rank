import collections
import random
import time

import geopy.distance

import common.settings
import common.utils

millisecond_in_hour = 60 * 60 * 1000


def time_to_timestamp(tweet_time):
    struct_time = time.strptime(tweet_time, '%a %b %d %H:%M:%S +0000 %Y')
    return int(time.mktime(struct_time) * 1000)


def window_by_nearby(tweets, interval=4):
    interval *= millisecond_in_hour
    nearby_tweet_indexes = collections.deque()
    right_tweet_index_iter = iter(range(len(tweets)))
    for tweet_index in range(len(tweets)):
        tweet_time = float(tweets[tweet_index]["timestamp_ms"])

        # remove from left
        while nearby_tweet_indexes:
            left_tweet_index = nearby_tweet_indexes[0]
            left_tweet_time = float(tweets[left_tweet_index]["timestamp_ms"])
            if (tweet_time - left_tweet_time) / interval < 1:
                break
            nearby_tweet_indexes.popleft()

        # add to right
        right_tweet_index = next(right_tweet_index_iter, None)
        while right_tweet_index:
            right_tweet_time = float(tweets[right_tweet_index]["timestamp_ms"])
            if (right_tweet_time - tweet_time) / interval > 1:
                break
            nearby_tweet_indexes.append(right_tweet_index)
            right_tweet_index = next(right_tweet_index_iter, None)
        yield tweet_index, nearby_tweet_indexes
        nearby_tweet_indexes = collections.deque(nearby_tweet_indexes)


def chunk_by_time(tweets, interval=1, sampled=1):
    print("chunking tweets by time")
    interval *= millisecond_in_hour
    start_time = float(tweets[0]["timestamp_ms"])
    end_time = float(tweets[-1]["timestamp_ms"])
    bucket_size = int((end_time - start_time) / interval) + 1
    buckets = [[] for _ in range(bucket_size)]
    for tweet in tweets:
        tweet_time = float(tweet["timestamp_ms"])
        index = int((tweet_time - start_time) / interval)
        buckets[index].append(tweet)

    for bucket_index in range(len(buckets)):
        random.shuffle(buckets[bucket_index])
        right_tweet_index = int(len(buckets[bucket_index]) * sampled)
        buckets[bucket_index] = buckets[bucket_index][:right_tweet_index]
    return buckets


def vicinity_of_event(tweet, radius):
    if "coordinates" not in tweet:
        return None

    tweet_coordinates = (tweet["coordinates"][0], tweet["coordinates"][1])
    event_location = common.settings.network.getfloatlist("EventLocation")
    distance = geopy.distance.great_circle(tweet_coordinates, event_location).km
    return distance < radius


# not sure if we should add plurals
personal_pronouns = ["i", "me", "mine", "my"]

# taken from https://www.mltcreative.com/blog/social-media-minute-big-a-list-of-twitter-slang-and-definitions/
twitter_slangs = open("data/twitter-slangs.txt").readlines()


def remove_spam(tweets):
    print("removing tweet spam")
    filtered_tweets = []
    for tweet in tweets:
        tokens = common.utils.tokenize_text(tweet["text"])
        if not any(word in tokens for word in personal_pronouns):
            if not any(word in tweet["text"] for word in twitter_slangs):
                if len(tokens) > 4:
                    filtered_tweets.append(tweet)
    return filtered_tweets
