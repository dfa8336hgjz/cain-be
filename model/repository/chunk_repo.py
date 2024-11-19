
from mysql.connector.aio import MySQLConnectionAbstract, Error
from errno import errorcode

from db.mysql_db import get_mysql_connection
from schema.chunk_schema import BaseChunk


class ChunkRepository:
    def __init__(self):
        self.cnx: MySQLConnectionAbstract = get_mysql_connection()
    
    async def find_chunks_has_words(self, keyword: str, file_id: str) -> list[BaseChunk]:
        try:
            query = """
            SELECT * 
            FROM chunks
            WHERE file_id = %s
            AND lower(content) LIKE lower(%s)
            """

            async with await self.cnx.cursor() as cur:
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
            print(e)