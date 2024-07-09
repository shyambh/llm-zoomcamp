import json
from pathlib import Path
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")
es.info()

API_KEY="abcdefgh"
PATH_TO_DATA = Path("data/documents.json")

documents = []

with open(PATH_TO_DATA, "r") as file:
    documents_file = json.load(file)

documents = []

# Flatten the json file
for course in documents_file:
    course_name = course["course"]

    for doc in course["documents"]:
        doc["course"] = course_name
        documents.append(doc)

# Indexing the elasticsearch
index_settings = {
    "settings": {"number_of_shards": 1, "number_of_replicas": 0},
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "section": {"type": "text"},
            "question": {"type": "text"},
            "course": {"type": "keyword"},
        }
    },
}

index_name = "course-questions"
response = es.indices.create(index=index_name, body=index_settings)

response

pass
