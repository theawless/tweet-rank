from twarc import Twarc

from common.mongo import tweets_collection
from common.settings import download_settings

twitter = Twarc(download_settings.getstring("TwitterConsumerKey"),
                download_settings.getstring("TwitterConsumerSecret"),
                download_settings.getstring("TwitterAccessKey"),
                download_settings.getstring("TwitterAccessSecret"))


def download():
    print("downloading")
    count = 0
    total_count = 0
    tweets = []
    for tweet in twitter.filter(track=download_settings.getstring("Query")):
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
