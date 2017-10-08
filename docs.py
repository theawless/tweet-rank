from utils import compute_similarity_matrix


def filter_docs(docs):
    filtered_docs = []
    for doc in docs:
        if "twitter.com" not in doc["expanded_url"]:
            filtered_docs.append(doc)
    return filtered_docs


def hydrate_docs(docs):
    for doc in docs:
        doc["text"] = "get content using Bing Search / URL"


doc_similarity_matrix = None


def get_doc_similarity_matrix(docs):
    global doc_similarity_matrix
    if doc_similarity_matrix is None:
        doc_similarity_matrix = compute_similarity_matrix([doc['text'] for doc in docs])
    return doc_similarity_matrix
