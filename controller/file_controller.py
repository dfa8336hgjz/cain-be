
import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException

from mysql.connector import Error
from db.mysql_db import get_mysql_connection
from schema.chunk_schema import BaseChunk
from schema.file_schema import BaseFile

DRIVE_FOLDER = os.getenv("DRIVE_FOLDER")

class FileController:
    def __init__(self):
        pass

    async def save_file_to_server(self, file: UploadFile, notebook_id: str):
        # Save file to disk
        file_id = "doc-" + str(uuid.uuid4())
        file_folder = os.path.join(DRIVE_FOLDER, notebook_id, file_id)

        if not os.path.exists(file_folder):
            os.makedirs(file_folder)  # Ensure the directory is created

        ext = file.filename.split(".")[-1]
        file_path = os.path.join(file_folder, "raw." + ext)

        # Use aiofiles to handle file operations asynchronously
        async with await aiofiles.open(file_path, "wb") as out_file:
            while content := await file.read(1024):  # Read and write the file in chunks
                await out_file.write(content)

        connector = await get_mysql_connection()
        try:
            query = "SELECT * FROM file WHERE file_id = %s"

            async with await connector.cursor() as cur:
                await cur.execute(query, (file_id,))
                rows = await cur.fetchall()
                results = [
                    BaseFile(
                        file_id=file_id,
                        file_name=file.filename,
                        notebook_id=notebook_id,
                        extensions=ext,
                        file_path=file_path
                    )
                    for row in rows
                ]
                return results
        except Error as err:
            raise HTTPException(status_code=400, detail=f"Failed to get notebooks: {err.msg} ")

        return file_id

    async def add_multiple_chunks(self, chunks: list[BaseChunk]):
        connector = await get_mysql_connection()
        try:
            query = ("INSERT INTO chunks (chunk_id, content, file_id)"
                     "VALUES (%s, %s, %s)")
            async with await connector.cursor() as cur:
                data = []
                for chunk in chunks:
                    data.append((chunk.chunk_id, chunk.content, chunk.file_id))
                await cur.executemany(query, data)
        except Error as e:
            raise HTTPException(status_code=400, detail=f"Failed to add chunks: {e.msg}")