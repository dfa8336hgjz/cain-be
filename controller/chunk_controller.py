import os
from unittest import result
from core.nlp.langchain_google_connector import get_embedding
from db.weaviate_db import get_langchain_weaviate_vectorstore
from schema.chunk_schema import BaseChunk
from langchain_core.documents.base import Document
from weaviate.collections.classes.filters import Filter
import weaviate
from weaviate.classes.init import Auth

class ChunkController:
    def __init__(self, app_controller):
        self.embedding = get_embedding()
        self.controller = app_controller

    async def add_to_vectorstores(self, chunks: list[BaseChunk]):
        try:
            with get_langchain_weaviate_vectorstore(self.embedding) as vectorstore:
                docs = []
                for item in chunks:
                    langchain_doc = Document(
                        page_content=item.content,
                        metadata={
                            'chunk_id': item.chunk_id,
                            'file_id': item.file_id,
                            'notebook_id': item.notebook_id
                        }
                    )
                    docs.append(langchain_doc)
                await vectorstore.aadd_documents(docs)
        except Exception as e:
            print("Weaviate error: ", e)

    async def delete_from_vectorstores_by_file_id(self, file_id):
        try:
            client = weaviate.connect_to_weaviate_cloud(
                cluster_url=os.getenv("WEAVIATE_URL"),
                auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY"))
            )
            query = f"""{{
                        Get {{
                            Cain(where: {{path: ["file_id"], operator: Equal, valueString: "{file_id}"}}) 
                            {{
                                _additional
                                {{
                                    id
                                }}
                            }}
                        }}
                    }}"""
            
            results = client.graphql_raw_query(query)
            all_chunk = client.collections.get("Cain")
            for result in results.get.get("Cain"):
                current_id = result.get("_additional").get("id")
                all_chunk.data.delete_by_id(current_id)
            client.close()

        except Exception as e:
            print("Weaviate error: ", e)

    async def delete_from_vectorstores_by_notebook_id(self, notebook_id):
        try:
            client = weaviate.connect_to_weaviate_cloud(
                cluster_url=os.getenv("WEAVIATE_URL"),
                auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY"))
            )
            query = f"""{{
                        Get {{
                            Cain(where: {{path: ["notebook_id"], operator: Equal, valueString: "{notebook_id}"}}) 
                            {{
                                _additional
                                {{
                                    id
                                }}
                            }}
                        }}
                    }}"""
            
            results = client.graphql_raw_query(query)
            all_chunk = client.collections.get("Cain")
            for result in results.get.get("Cain"):
                current_id = result.get("_additional").get("id")
                all_chunk.data.delete_by_id(current_id)
            client.close()

        except Exception as e:
            print("Weaviate error: ", e)

    async def delete_all_from_vectorstores(self):
        try:
            client = weaviate.connect_to_weaviate_cloud(
                cluster_url=os.getenv("WEAVIATE_URL"),
                auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY"))
            )
            query = f"""{{
                        Get {{
                            Cain
                            {{
                                _additional
                                {{
                                    id
                                }}
                            }}
                        }}
                    }}"""
            
            results = client.graphql_raw_query(query)
            all_chunk = client.collections.get("Cain")
            for result in results.get.get("Cain"):
                current_id = result.get("_additional").get("id")
                all_chunk.data.delete_by_id(current_id)
            client.close()

        except Exception as e:
            print("Weaviate error: ", e)