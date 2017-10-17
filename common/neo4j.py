import py2neo
from tqdm import tqdm

import common.settings

graph = py2neo.Graph(host=common.settings.neo4j.getstring("Host"),
                     http_port=common.settings.neo4j.getint("Port"),
                     username=common.settings.neo4j.getstring("Username"),
                     password=common.settings.neo4j.getstring("Password"))
try:
    graph.schema.create_uniqueness_constraint("tweet", 'id_str')
except:
    pass
try:
    graph.schema.create_uniqueness_constraint("user", 'id_str')
except:
    pass
try:
    graph.schema.create_uniqueness_constraint("doc", 'id_str')
except:
    pass


def write_neo(nodes, edges):
    print("writing graph to neo")
    count = 0
    graph.delete_all()
    transaction = graph.begin()
    for f, t, data in tqdm(edges):
        count += 1
        node_from = py2neo.Node(nodes[f]["label"], **{**nodes[f], **{"id_str": f}})
        node_to = py2neo.Node(nodes[t]["label"], **{**nodes[t], **{"id_str": t}})
        edge = py2neo.Relationship(node_from, data["label"], node_to, **data)
        transaction.merge(edge)

        if count == common.settings.neo4j.getint("TransactionsBeforeCommit"):
            count = 0
            transaction.commit()
            transaction = graph.begin()
    transaction.commit()
