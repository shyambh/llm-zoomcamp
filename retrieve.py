import json
from pathlib import Path
from tqdm.auto import tqdm
from elasticsearch import Elasticsearch
from openai import OpenAI


PATH_TO_DATA = Path("data/documents.json")

documents = []

# Instantiate the OpenAI client
openai_client = OpenAI()

# Building a prompt
context_template = """
Section: {section}
Question: {question}
Answer: {text}
""".strip()


# Building the prompt template which includes placeholders for question and the context
prompt_template = """
You're a course teaching assistant. Answer the user QUESTION based on CONTEXT - the documents retrieved from our FAQ database. 
Only use the facts from the CONTEXT. Don't use other information outside of the provided CONTEXT. "

QUESTION: {user_question}

CONTEXT:

{context}
""".strip()


def retrieve_documents(user_question, index_name="course-questions", max_results=5):
    fetched_documents = []

    search_query = {
        "size": max_results,
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

    fetched_from_es = es.search(index=index_name, body=search_query)
    fetched_documents = [hit["_source"] for hit in fetched_from_es["hits"]["hits"]]

    return fetched_documents


def build_context(documents):
    context_result = ""

    for doc in documents:
        doc_str = context_template.format(**doc)
        context_result += "\n\n" + doc_str

    context = context_result.strip()
    return context


def build_prompt(prompt_template: str, user_question, documents):
    context = build_context(documents)
    prompt = prompt_template.format(user_question=user_question, context=context)

    return prompt


def ask_openai(client: OpenAI, prompt, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )
    answer = response.choices[0].message.content
    return answer


def qa_bot(user_question):
    context_docs = retrieve_documents(user_question)
    prompt = build_prompt(prompt_template, user_question, context_docs)
    answer = ask_openai(openai_client, prompt)
    return answer


# Initialize ElasticSearch
es = Elasticsearch("http://localhost:9200")


def create_index_if_not_already_created(index_name, path_to_data, index_setting):

    index_name = "course-questions"
    if not es.indices.exists(index=index_name):
        with open(PATH_TO_DATA, "r", encoding="UTF-8") as file:
            documents_file = json.load(file)

        # Flatten the json file
        for course in documents_file:
            course_name = course["course"]

            for doc in course["documents"]:
                doc["course"] = course_name
                documents.append(doc)

        es.indices.create(index=index_name, body=index_settings)

        for doc in tqdm(documents):
            es.index(index=index_name, document=doc)


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

# create_index_if_not_already_created("course-questions", PATH_TO_DATA, index_settings)

# # Retrieving answer from the docs
# user_question = """
# how can I run kafka?
# """

# answer = qa_bot(user_question)
# print(answer)


def main():
    create_index_if_not_already_created(
        "course-questions", PATH_TO_DATA, index_settings
    )

    # Retrieving answer from the docs
    user_question = """
    how can I run kafka?
    """

    answer = qa_bot(user_question)
    print(answer)


if __name__ == "__main__":
    main()
