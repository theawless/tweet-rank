import urllib.request

import bs4
import google

import common.mongo

queries = open("data/sample-queries.txt").readlines()


def fill_doc(url, doc):
    try:
        html = urllib.request.urlopen(url)
        soup = bs4.BeautifulSoup(html)
        doc["id_str"] = url
        doc["text"] = soup.title.text
        common.mongo.docs_collection.update_one({"id_str": doc["id_str"]}, {"$set": doc}, upsert=True)
        print(doc)
    except Exception:
        pass


def fill_docs():
    for query in queries:
        print("searching for", query)
        for url in google.search(query, num=1, stop=3):
            doc = {"query": query}
            fill_doc(url, doc)


if __name__ == '__main__':
    fill_docs()
