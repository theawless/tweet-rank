from twarc import Twarc

from common.mongo import tweets_collection

twitter = Twarc("consumer key",
                "consumer secret",
                "access key",
                "access secret")


def download():
    print("downloading")
    count = 0
    total_count = 0
    tweets = []
    for tweet in twitter.filter(track="query"):
        count += 1
        total_count += 1
        tweets.append(tweet)
        print(total_count, end="\r")

        if count == 5000:
            tweets_collection.insert_many(tweets)
            tweets.clear()
            count = 0


if __name__ == '__main__':
    download()
