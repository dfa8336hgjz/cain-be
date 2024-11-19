from __future__ import annotations
from typing import *

from langchain_core.documents import Document

from mysql.connector.aio import MySQLConnectionAbstract

class ChunkRetriever():
    def __init__(self, repositories):
        super().__init__()
        self.repositories = repositories

    def langchain_retrieve(self, keyword: str, file_ids: list[str]) -> list[Document]:
        return self.repositories.chunk_vector_repo.chunk_retrieve_for_langchain(keyword, file_ids)

    async def retrieve(self, keyword, file_ids: list[str]):
        return await self.repositories.chunk_vector_repo.chunks_vector_search(keyword, file_ids)

    async def find(self, keyword: str, file_id: str, cnx: MySQLConnectionAbstract):
        words = keyword.lower()
        return await self.repositories.chunk_repo.find_chunks_has_words(words, file_id, cnx)