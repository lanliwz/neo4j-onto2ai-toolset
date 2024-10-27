import os

neo4j_bolt_url = os.getenv("Neo4jFinDBUrl")
username = os.getenv("Neo4jFinDBUserName")
password = os.getenv("Neo4jFinDBPassword")
neo4j_db_name = 'rdfmodel2'

auth_data = {'uri': neo4j_bolt_url,
             'database': neo4j_db_name,
             'user': username,
             'pwd': password}