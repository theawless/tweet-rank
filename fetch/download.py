import twarc
from tqdm import tqdm

import common.mongo
import common.settings

twitter = twarc.Twarc(common.settings.download.getstring("TwitterConsumerKey"),
                      common.settings.download.getstring("TwitterConsumerSecret"),
                      common.settings.download.getstring("TwitterAccessKey"),
                      common.settings.download.getstring("TwitterAccessSecret"))


def download():
    print("downloading full tweets")
    count = 0
    tweets = []
    for tweet in tqdm(twitter.filter(track=common.settings.download.getstring("Query"))):
        count += 1
        tweets.append(tweet)
        if count == common.settings.download.getint("TweetsBeforeCommit"):
            common.mongo.tweets_collection.insert_many(tweets)
            tweets.clear()
            count = 0


if __name__ == '__main__':
    download()
