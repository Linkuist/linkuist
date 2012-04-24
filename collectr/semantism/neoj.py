# -*- coding: utf-8 -*-
"""


"""
NEO4J_DIR="/home/benoit/projs/collectr/neo4j"

from neo4j import GraphDatabase
GraphDatabatabase(NEO4J_DIR)

for word in ('public', 'internet', 'google'):
    with db.transaction:
        node = db.node()
        node['word'] = word

