from __future__ import annotations
from typing import *

from langchain_core.documents import Document

from mysql.connector.aio import MySQLConnectionAbstract
from model.repository.repo_manager import RepositoryManager

class ChunkRetriever():
    def __init__(self, repositories: RepositoryManager):
        super().__init__()
        self.repositories = repositories

    def langchain_retrieve(self, keyword: str, document_ids: List[str]) -> List[Document]:
        return self.repositories.chunk_vector_repo.chunk_retrieve_for_langchain(keyword, document_ids)

    async def retrieve(self, keyword, document_ids: List[str]):
        return await self.repositories.chunk_vector_repo.chunks_vector_search(keyword, document_ids)

    async def find(self, keyword: str, document_id: str, cnx: MySQLConnectionAbstract):
        words = keyword.lower()
        return await self.repositories.chunk_repo.find_chunks_has_words(words, document_id, cnx)