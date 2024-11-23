import uuid
from fastapi import Depends
from langchain_text_splitters import RecursiveCharacterTextSplitter
from docx import Document as DocxDocument

from schema.chunk_schema import BaseChunk
from mysql.connector.aio import MySQLConnectionAbstract
from .base_text_splitter import BaseTextSplitter

class WordTextSplitter(BaseTextSplitter):
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
        doc = DocxDocument(self.filepath)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)

        text_content = "\n".join(full_text)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=overlap
        )
        splits = splitter.split_text(text_content)

        results = []
        for i, split in enumerate(splits):
            chunk_id = "chunk-" + str(uuid.uuid4())
            chunk = BaseChunk(
                chunk_id=chunk_id,
                content=split,
                file_id=self.file_id,
            )
            results.append(chunk)
        return results
