import json
from pathlib import Path
from tqdm.auto import tqdm
from elasticsearch import Elasticsearch


PATH_TO_DATA = Path("data/documents.json")

documents = []


def retrieve_documents(query, index_name="course-questions", max_results=5):
    search_query = {
        "size": 5,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": user_question,
                        "fields": ["question^3", "text", "section"],
                        "type": "best_fields",
                    }
                },
                "filter": {"term": {"course": "data-engineering-zoomcamp"}},
            }
        },
    }

    response = es.search(index=index_name, body=search_query)

    documents = [hit["_source"] for hit in response["hits"]["hits"]]
    return documents


with open(PATH_TO_DATA, "r") as file:
    documents_file = json.load(file)

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


# Initialize ElasticSearch
es = Elasticsearch("http://localhost:9200")


# Create Index
index_name = "course-questions"
# response = es.indices.create(index=index_name, body=index_settings)


for doc in tqdm(documents):
    es.index(index=index_name, document=doc)

# Retrieving the docs
user_question = "Will I get a certificate at the end of the course?"
response = retrieve_documents(user_question)

for doc in response:
    print(f"Section: {doc['section']}")
    print(f"Question: {doc['question']}")
    print(f"Answer: {doc['text'][:60]}...\n")
