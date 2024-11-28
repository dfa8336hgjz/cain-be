from core.nlp.langchain_google_connector import get_embedding
from db.weaviate_db import get_langchain_weaviate_vectorstore
from schema.chunk_schema import BaseChunk
from langchain_core.documents.base import Document

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
                        }
                    )
                    docs.append(langchain_doc)
                await vectorstore.aadd_documents(docs)
        except Exception as e:
            print("Weaviate error: ", e)