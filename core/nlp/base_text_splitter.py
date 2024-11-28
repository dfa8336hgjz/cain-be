from __future__ import annotations

import logging
from typing import *
from abc import abstractmethod

from mysql.connector import Error

from schema.chunk_schema import BaseChunk
from mysql.connector.aio import MySQLConnectionAbstract

class BaseTextSplitter:
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
        self.chunks = None
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.filepath = filepath
        self.file_id = file_id
        self.notebook_id = notebook_id
        self.sql_connector = connector
        self.controller = controller

    def process(self):
        self.chunks = self.split(self.chunk_size, self.overlap)

    async def save(self):
        if self.chunks:
            try:
                await self.controller.chunk_controller.add_to_vectorstores(self.chunks)
            except Error as e:
                logging.error(str(e))
                raise e

    @abstractmethod
    def split(self, chunk_size: int, overlap: int) -> list[BaseChunk]:
        pass

    async def process_and_save(self):
        self.process()
        await self.save()