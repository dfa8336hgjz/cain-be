import weaviate
import os
from dotenv import load_dotenv
from contextlib import contextmanager
from langchain_weaviate.vectorstores import WeaviateVectorStore
from weaviate.classes.init import Auth

load_dotenv()


@contextmanager
def get_langchain_weaviate_vectorstore(embedding=None):
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY"))
    )
    if embedding:
        vectorstore = WeaviateVectorStore(client, os.getenv("WEAVIATE_DOCUMENT_DATABASE"),
                                          os.getenv("WEAVIATE_DOCUMENT_TEXT_KEY"),
                                          embedding=embedding)
    else:
        vectorstore = WeaviateVectorStore(client, os.getenv("WEAVIATE_DOCUMENT_DATABASE"),
                                          os.getenv("WEAVIATE_DOCUMENT_TEXT_KEY"))
    try:
        yield vectorstore
    finally:
        vectorstore = None
        client.close()


@contextmanager
def get_weaviate_client(embedding=None):
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY"))
    )
    try:
        yield client
    finally:
        client.close()
