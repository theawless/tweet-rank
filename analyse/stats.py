import matplotlib.pyplot as plt

from analyse import tweets, users

user_ids = set()
tweet_ids = set()

most_favorited_tweet = None
most_retweeted_tweet = None


def load_tweets():
    global most_favorited_tweet, most_retweeted_tweet
    for tweet in tweets:
        if tweet['id'] not in tweet_ids:
            tweets.append(tweet)
            tweet_ids.add(tweet['id'])

            # For computing most favorited/retweeted tweet
            if most_favorited_tweet is None:
                most_favorited_tweet = tweet
            else:
                if tweet['favorite_count'] > most_favorited_tweet['favorite_count']:
                    most_favorited_tweet = tweet

            if most_retweeted_tweet is None:
                most_retweeted_tweet = tweet
            else:
                if tweet['retweet_count'] > most_favorited_tweet['retweet_count']:
                    most_retweeted_tweet = tweet

                    # Add user to user's list
            user = tweet['user']
            if user['id'] not in user_ids:
                users.append(user)
                user_ids.add(user['id'])


# TODO: Implement filtering
def is_spam(tweet):
    return False


def spam_percent(s):
    total = s['spam'] + s['non_spam']
    return (float(s['spam']) / total) * 100


# TODO: Show hours on time axis
# Interval is in terms of seconds
# Default interval is 60 seconds
def spam_distribution(interval=60):
    tweet_bins = []
    INTERVAL = interval * 1000

    bin_start = int(tweets[0]['timestamp_ms'])
    tweet_bins.append([bin_start, {'spam': 0, 'non_spam': 0}])

    for tweet in tweets[:10]:
        tweet_time = int(tweet['timestamp_ms'])

        # If the tweet belongs to this bin, append it into the bin
        if tweet_time < bin_start + INTERVAL:
            if is_spam(tweet):
                tweet_bins[-1][1]['spam'] += 1
            else:
                tweet_bins[-1][1]['non_spam'] += 1
            continue

        # Otherwise, create new empty bins until this tweet fits into a bin
        bin_start += INTERVAL
        while tweet_time > bin_start + INTERVAL:
            tweet_bins.append([bin_start, {'spam': 0, 'non_spam': 0}])
            bin_start += INTERVAL

            # create a bin with the tweet
        tweet_bins.append([bin_start, {'spam': int(is_spam(tweet)), 'non_spam': int(not is_spam(tweet))}])

    print(tweet_bins)

    x = [t[0] for t in tweet_bins]
    y = [spam_percent(t[1]) for t in tweet_bins]

    plt.xlabel('Time')
    plt.ylabel('% Spam')
    plt.title('Spam Distribution')

    plt.hist(x, len(x), weights=y)
    plt.show()


def top_ten_hash_tags():
    hash_tags = {}
    for tweet in tweets:
        if 'entities' in tweet:
            for hash_tag in tweet['entities']['hashtags']:
                h = hash_tag['text']
                if h in hash_tags:
                    hash_tags[h] += 1
                else:
                    hash_tags[h] = 1

    return sorted(hash_tags.items(), key=lambda x: x[1], reverse=True)[:10]


def tweet_count():
    return len(tweets)


def user_count():
    return len(users)


if __name__ == '__main__':
    load_tweets()
    print(len(tweets))
    print(len(users))
    print(most_favorited_tweet['favorite_count'])
    print(most_retweeted_tweet['retweet_count'])
    # spamDistribution(interval=1)
    # print(topTenHashTags())
