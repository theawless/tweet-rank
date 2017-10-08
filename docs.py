def filter_docs(docs):
    filtered_docs = []
    for doc in docs:
        if "twitter.com" not in doc["expanded_url"]:
            filtered_docs.append(doc)
    return filtered_docs


def hydrate_docs(docs):
    for doc in docs:
        doc["text"] = "get content using Bing Search / URL"
