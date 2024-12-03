
import os
from urllib.parse import quote_plus
import uuid
import aiofiles
import asyncio
from fastapi import UploadFile, HTTPException

from mysql.connector import Error
from core.nlp.docx_text_splitter import WordTextSplitter
from core.nlp.pdf_text_splitter import PdfTextSplitter
from db.mysql_db import get_mysql_connection
from mysql.connector.aio import MySQLConnectionAbstract

from schema.file_schema import BaseFile

DRIVE_FOLDER = os.getenv("DRIVE_FOLDER")

class FileController:
    def __init__(self, app_controller):
        self.controller = app_controller

    async def save_file_to_server(self, file: UploadFile, notebook_id: str):
        # Save file to disk
        file_id = "doc-" + str(uuid.uuid4())
        file_folder = os.path.join(DRIVE_FOLDER, notebook_id, )
        if not os.path.exists(file_folder):
            os.makedirs(file_folder)  # Ensure the directory is created

        file_path = os.path.join(file_folder, file.filename)
        ext = file.filename.split(".")[-1]

        if ext not in ["pdf", "docx"]:
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Use aiofiles to handle file operations asynchronously
        async with aiofiles.open(file_path, "wb") as out_file:
            while content := await file.read(1024):  # Read and write the file in chunks
                await out_file.write(content)

        connector = await get_mysql_connection()
        try:
            query = "INSERT INTO file (file_id, notebook_id, file_name, extensions, file_path) VALUES (%s, %s, %s, %s, %s)"
            async with await connector.cursor() as cur:
                await cur.execute(query, (file_id, notebook_id, file.filename, ext, file_path))
                await connector.commit()
            
            await self.handle_file_uploaded(file_path, file_id, notebook_id, connector)

            return BaseFile(file_id=file_id, notebook_id=notebook_id, file_name=file.filename, extensions=ext, file_path=file_path)
        except Error as err:
            await connector.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to save notebooks: {err.msg} ")
        finally:
            await connector.close()

    async def handle_file_uploaded(self, file_path: str, file_id: str, notebook_id: str, connector: MySQLConnectionAbstract):
        text_splitter = None
        if file_path.endswith(".pdf"):
            text_splitter = PdfTextSplitter(
                filepath=file_path,
                file_id=file_id,
                notebook_id=notebook_id,
                chunk_size=1000,
                overlap=200,
                connector=connector,
                controller=self.controller
            )
        elif file_path.endswith(".docx"):
            text_splitter = WordTextSplitter(
                filepath=file_path,
                file_id=file_id,
                notebook_id=notebook_id,
                chunk_size=1000,
                overlap=200,
                connector=connector,
                controller=self.controller
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid file type")

        await text_splitter.process_and_save()

    async def delete_file_in_notebook(self, file_id: str, notebook_id: str):
        connector = await get_mysql_connection()
        try:
            query = "DELETE FROM file WHERE file_id = %s and notebook_id = %s"
            async with await connector.cursor() as cur:
                await cur.execute(query, (file_id, notebook_id,))
                await connector.commit()

            await self.controller.chunk_controller.delete_from_vectorstores_by_file_id(file_id)

        except Error as err:
            await connector.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to save notebooks: {err.msg} ")
        finally:
            await connector.close()

    async def delete_all_files_in_notebook(self, notebook_id: str):
        connector = await get_mysql_connection()
        try:
            query = "DELETE FROM file WHERE notebook_id = %s"
            async with await connector.cursor() as cur:
                await cur.execute(query, (notebook_id,))
                await connector.commit()

            await self.controller.chunk_controller.delete_from_vectorstores_by_notebook_id(notebook_id)
        except Exception as e:
            raise e