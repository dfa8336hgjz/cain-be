from __future__ import annotations

import uuid
import threading
from fastapi import Depends
from langchain_community.document_loaders.parsers.pdf import PyMuPDFParser
from langchain_core.documents.base import Blob
from langchain_text_splitters import RecursiveCharacterTextSplitter

from mysql.connector.aio import MySQLConnectionAbstract
from schema.chunk_schema import BaseChunk
from .base_text_splitter import BaseTextSplitter

class PdfTextSplitter(BaseTextSplitter):
    def __init__(
        self,
        filepath: str,
        file_id: str,
        notebook_id: str,
        chunk_size: int,
        overlap: int,
        connector: MySQLConnectionAbstract,
        controller
    ):
        super().__init__(
            filepath, file_id, notebook_id, chunk_size, overlap, connector, controller
        )

    def split(self, chunk_size: int, overlap: int) -> list[BaseChunk]:
        parser = PyMuPDFParser()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=overlap
        )
        blob = Blob.from_path(self.filepath)
        docs = parser.lazy_parse(blob)
        splits = splitter.split_documents(docs)
        results = []
        for i, split in enumerate(splits):
            chunk_id = "chunk-" + str(uuid.uuid4())
            chunk = BaseChunk(
                chunk_id=chunk_id,
                content=split.page_content,
                file_id=self.file_id,
            )
            results.append(chunk)
        return results
