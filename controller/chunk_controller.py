from mysql.connector.aio import Error
from fastapi import HTTPException
from core.nlp.langchain_google_connector import get_embedding
from db.mysql_db import get_mysql_connection
from db.weaviate_db import get_langchain_weaviate_vectorstore
from mysql.connector.aio import MySQLConnectionAbstract
from schema.chunk_schema import BaseChunk
from langchain_core.documents.base import Document

class ChunkController:
    def __init__(self, app_controller):
        self.embedding = get_embedding()
        self.controller = app_controller

    async def find_chunks_has_words(self, keyword: str, file_id: str) -> list[BaseChunk]:
        connector = await get_mysql_connection()
        try:
            query = """
            SELECT * 
            FROM chunk
            WHERE file_id = %s
            AND lower(content) LIKE lower(%s)
            """

            async with await connector.cursor() as cur:
                await cur.execute(query, (file_id, f'%{keyword}%'))
                rows = await cur.fetchall()
                results = [
                    BaseChunk(
                        chunk_id=row[0],
                        content=row[1],
                        file_id=row[2]
                    )
                    for row in rows
                ]
                return results

        except Error as e:
            raise HTTPException(status_code=400, detail=f"Failed to get chunks: {e.msg}")
        finally:
            await connector.close()

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

    
    async def add_multiple_chunks(self, chunks: list[BaseChunk], connector: MySQLConnectionAbstract):
        try:
            query = ("INSERT INTO chunk (chunk_id, content, file_id)"
                     "VALUES (%s, %s, %s)")
            async with await connector.cursor() as cur:
                data = []
                for chunk in chunks:
                    data.append((chunk.chunk_id, chunk.content, chunk.file_id))
                await cur.executemany(query, data)
                await connector.commit()
        except Error as e:
            await connector.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to add chunks: {e.msg}")
        finally:
            await connector.close()