
from langchain_core.documents.base import Document
from typing import List
from weaviate.classes.query import Filter
from db.weaviate_db import get_langchain_weaviate_vectorstore
from schema.chunk_schema import BaseChunk


class ChunkVectorRepository:
    def __init__(self, embedding):
        super().__init__()
        self.embedding = embedding

    def chunk_retrieve_for_langchain(self, s: str, document_ids: List[str]) -> List[Document]:
        try:
            with get_langchain_weaviate_vectorstore(self.embedding) as vectorstore:
                document_filter = Filter.by_property("file_id").contains_any(document_ids)
                docs = vectorstore.similarity_search(s, filters=document_filter)
                return docs
        except Exception as e:
            print(e)

    async def chunks_vector_search(self, s: str, document_ids: List[str]) -> List[BaseChunk]:
        try:
            with get_langchain_weaviate_vectorstore(self.embedding) as vectorstore:
                document_filter = Filter.by_property("file_id").contains_any(document_ids)
                docs = await vectorstore.asimilarity_search(s, filters=document_filter)
                chunks = []
                for doc in docs:
                    chunk = BaseChunk(chunk_id=doc.metadata['chunk_id'],
                                      content=doc.page_content,
                                      document_id=doc.metadata['file_id'],
                                      order_in_ref=doc.metadata['order_in_file'])
                    chunks.append(chunk)
                return chunks
        except Exception as e:
            print(e)