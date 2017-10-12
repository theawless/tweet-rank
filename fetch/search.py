from urllib.request import urlopen

from bs4 import BeautifulSoup
from google import search

from common.mongo import docs_collection

queries = open("data/sample-queries.txt").readlines()


def fill_doc(url, doc):
    try:
        print(url)
        html = urlopen(url)
        soup = BeautifulSoup(html)
        doc["id_str"] = url
        doc["text"] = soup.title.text
        print(doc)
        docs_collection.update_one({"id_str": doc["id_str"]}, {"$set": doc}, upsert=True)
    except Exception:
        pass


def fill_docs():
    for query in queries:
        print("searching for", query)
        for url in search(query, num=1, stop=3):
            doc = {"query": query}
            fill_doc(url, doc)


if __name__ == '__main__':
    fill_docs()
