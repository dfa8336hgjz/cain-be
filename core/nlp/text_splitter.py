from __future__ import annotations

import logging
from typing import *
from abc import abstractmethod

from mysql.connector import Error
from mysql.connector.aio import MySQLConnectionAbstract
from sqlalchemy.exc import SQLAlchemyError

from controller.app_controller import AppController
from schema.chunk_schema import BaseChunk



class BaseTextSplitter:
    def __init__(
        self,
        filepath: str,
        file_id: str,
        project_id: str,
        chunk_size: int,
        overlap: int,
        controller: AppController,
    ):
        self.splits = None
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.controller = controller

    def process(self):
        self.splits = self.split(self.chunk_size, self.overlap)

    async def save(self):
        if self.splits:
            try:
                await self.controller.file_controller.add_multiple_chunks(
                    self.splits
                )
                await self.repositories.chunk_vector_repo.add_many(self.splits)
                await self.cnx.commit()
            except Error as e:
                logging.error(str(e))
                await self.cnx.rollback()
                raise e
            finally:
                await self.cnx.close()

    @abstractmethod
    def split(self, chunk_size: int, overlap: int) -> list[BaseChunk]:
        pass

