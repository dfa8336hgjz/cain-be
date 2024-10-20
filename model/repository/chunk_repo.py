from typing import List
from mysql.connector.aio import MySQLConnectionAbstract, Error
from errno import errorcode

from db.mysql_db import get_mysql_connection
from schema.chunk_schema import BaseChunk


class ChunkRepository:
    def __init__(self):
        self.cnx: MySQLConnectionAbstract = get_mysql_connection()
    
    async def find_chunks_has_words(self, keyword: str, document_id: str) -> List[BaseChunk]:
        try:
            query = """
            SELECT * 
            FROM chunks
            WHERE document_id = %s
            AND lower(content) LIKE lower(%s)
            """

            async with await self.cnx.cursor() as cur:
                await cur.execute(query, (document_id, f'%{keyword}%'))
                rows = await cur.fetchall()
                results = [
                    BaseChunk(
                        chunk_id=row[0],
                        content=row[1],
                        created_at=row[2],
                        updated_at=row[3],
                        order_in_ref=row[4],
                        document_id=row[5]
                    )
                    for row in rows
                ]
                return results

        except Error as e:
            print(e)