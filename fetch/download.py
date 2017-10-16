import twarc

import common.mongo
import common.settings

twitter = twarc.Twarc(common.settings.download_settings.getstring("TwitterConsumerKey"),
                      common.settings.download_settings.getstring("TwitterConsumerSecret"),
                      common.settings.download_settings.getstring("TwitterAccessKey"),
                      common.settings.download_settings.getstring("TwitterAccessSecret"))


def download():
    print("downloading")
    count = 0
    total_count = 0
    tweets = []
    for tweet in twitter.filter(track=common.settings.download_settings.getstring("Query")):
        count += 1
        total_count += 1
        tweets.append(tweet)
        print(total_count, end="\r")

        if count == 5000:
            common.mongo.tweets_collection.insert_many(tweets)
            tweets.clear()
            count = 0


if __name__ == '__main__':
    download()
