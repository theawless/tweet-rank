# if __name__ == '__main__':
#     from fetch.assemble import assemble
#
#     assemble()

if __name__ == '__main__':
    from network.main import main

    main()

# import time
#
# import pymongo
#
# millisecond_in_hour = 60 * 60 * 1000
#
#
# def time_to_timestamp(tweet_time):
#     struct_time = time.strptime(tweet_time, '%a %b %d %H:%M:%S +0000 %Y')
#     return int(time.mktime(struct_time) * 1000)
#
#
# if __name__ == '__main__':
#     client = pymongo.MongoClient(host="localhost", port=27017)
#     database = client["vegas"]
#     tweets = database["full_tweets_new"].find({"timestamp_ms": {"$exists": True}},
#                                               sort=[("timestamp_ms", pymongo.ASCENDING)])
#     tweet = tweets[0]
#     start_time = float(tweet["timestamp_ms"])
#
#     count = 0
#     tweets_m_collection = database["tweets_j_new"]
#     for tweet in tweets:
#         tweet_time = float(tweet["timestamp_ms"])
#         index = int((tweet_time - start_time) / millisecond_in_hour)
#         if index == 77 or index == 73:
#             if "coordinates" in tweet:
#                 tweets_m_collection.insert(tweet)
#                 count += 1
#         if count == 17734:
#             break

# import subprocess
# import time
#
# import pymongo
#
# client = pymongo.MongoClient(host="localhost", port=27017)
# database = client["vegas"]
#
# if __name__ == '__main__':
#     docs = database["docs"].find()
#     for doc in docs:
#         print("doc id", doc["id_str"])
#         print("doc url", doc["url"])
#         doc["text"] = ""
#         name = "data/docs/" + doc["id_str"]
#         subprocess.call(["x-www-browser", doc["url"]])
#         subprocess.call(["gedit", name])
#         time.sleep(1)
#         with open(name, "r") as f:
#             for line in f:
#                 doc["text"] += line + "\n"
#         database["docs"].update_one({"id_str": doc["id_str"]}, {"$set": doc}, upsert=True)

# import pymongo
# import twarc
# from tqdm import tqdm
#
# client = pymongo.MongoClient(host="localhost", port=27017)
# database = client["vegas"]
# twitter = twarc.Twarc("MOPKpfkoTOn1naxRNufa5yT98",
#                       "7eK2ebL5RyZfUXo0V7S8WI4qbQwdxA5AuC7QoQqbmWPsmWNzXy",
#                       "912045458800988162-iYcr8fD9n5lXkNdsWaMaReEbP4kARgy",
#                       "t2xEXbHY86o2LLHCjr7lVcmWb3kaGJBTPaJ6hENT01MdC")
#
# ts = [tweet["id_str"] for tweet in database["tweets_j_new"].find()]
# for nt in tqdm(twitter.hydrate(ts)):
#     database["final_tweets"].update_one({"id_str": nt["id_str"]}, {"$set": nt}, upsert=True)

# import pymongo
# client = pymongo.MongoClient(host="localhost", port=27017)
# database = client["vegas"]
#
# for a in database["annotation_j"].find():
#     database["final_annotations"].update_one({"id_str": a["id_str"]}, {"$set": a}, upsert=True)
