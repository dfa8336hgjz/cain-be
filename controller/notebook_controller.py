import uuid

from mysql.connector import Error
from fastapi import HTTPException
from core.nlp.RAG_agent import RagAgent
from db.mysql_db import get_mysql_connection

from schema.file_schema import BaseFile
from schema.message_schema import BaseMessage
from schema.notebook_schema import BaseNotebook

class NotebookController:
    def __init__(self, app_controller):
        self.controller = app_controller
        
    async def get_all_notebooks_by_user_id(self, user_id: str) -> list[BaseNotebook]:
        connector = await get_mysql_connection()
        try:
            query = "SELECT * FROM notebook WHERE user_id = %s"

            async with await connector.cursor() as cur:
                await cur.execute(query, (user_id,))
                rows = await cur.fetchall()
                results = [
                    BaseNotebook(
                        notebook_id=row[0],
                        user_id=row[1],
                        title=row[2],
                        created_at=row[3],
                        last_access_at=row[4],
                    )
                    for row in rows
                ]
                return results
        except Error as err:
            raise HTTPException(status_code=400, detail=f"Failed to get notebooks: {err.msg}")
        finally:
            await connector.close()

    async def create_notebook_by_user_id(self, user_id: str, title: str):
        connector = await get_mysql_connection()
        notebook_id = f"notebook-{uuid.uuid4()}"
        try:
            query1 = "SELECT notebook_id FROM notebook WHERE title = %s and user_id = %s"
            query2 = "INSERT INTO notebook (notebook_id, user_id, title) VALUES (%s, %s, %s)"

            async with await connector.cursor() as cur:
                await cur.execute(query1, (title, user_id))
                notebook = await cur.fetchone()
                if notebook:
                    raise HTTPException(status_code=406, detail="Notebook already exists")
                
                await cur.execute(query2, (notebook_id, user_id, title if title else "Untitled notebook"))
                await connector.commit()
                return notebook_id
        except Error as err:
            await connector.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to create notebook: {err.msg}")
        finally:
            await connector.close()

    async def delete_notebook_by_id(self, notebook_id: str, user_id: str):
        connector = await get_mysql_connection()
        try:
            query = "DELETE FROM notebook WHERE notebook_id = %s and user_id = %s"
            async with await connector.cursor() as cur:
                await cur.execute(query, (notebook_id, user_id))
                await connector.commit()

            self.controller.chunk_controller.delete_from_vectorstores_by_notebook_id(notebook_id)
        except Error as err:
            await connector.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to delete notebook: {err.msg}")
        finally:
            await connector.close()

    async def get_notebook_by_id(self, notebook_id: str, user_id: str):
        connector = await get_mysql_connection()
        try:
            query = "SELECT * FROM notebook WHERE notebook_id = %s and user_id = %s"
            async with await connector.cursor() as cur:
                await cur.execute(query, (notebook_id, user_id))
                notebook = await cur.fetchone()
                if notebook:
                    return BaseNotebook(
                        notebook_id=notebook[0],
                        user_id=notebook[1],
                        title=notebook[2],
                        created_at=notebook[3],
                        last_access_at=notebook[4],
                    )
        except Error as err:
            raise HTTPException(status_code=400, detail=f"Failed to get notebook: {err.msg}")
        finally:
            await connector.close()

    async def update_notebook_access_time(self, notebook_id: str, user_id: str):
        connector = await get_mysql_connection()
        try:
            query = "UPDATE notebook SET last_access_at = NOW() WHERE notebook_id = %s and user_id = %s"
            async with await connector.cursor() as cur:
                await cur.execute(query, (notebook_id, user_id))
                await connector.commit()
        except Error as err:
            await connector.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to update notebook access time: {err.msg}")
        finally:
            await connector.close()

    async def update_notebook_title(self, notebook_id: str, user_id: str, title: str):
        connector = await get_mysql_connection()
        try:
            query = "UPDATE notebook SET title = %s WHERE notebook_id = %s and user_id = %s"
            async with await connector.cursor() as cur:
                await cur.execute(query, (title, notebook_id, user_id))
                await connector.commit()
        except Error as err:
            await connector.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to update notebook title: {err.msg}")
        finally:
            await connector.close()

    async def delete_message_history(self, notebook_id: str, user_id: str):
        connector = await get_mysql_connection()
        try:
            query1 = "SELECT notebook_id FROM notebook WHERE notebook_id = %s and user_id = %s"
            query2 = "DELETE FROM messages WHERE notebook_id = %s"
            async with await connector.cursor() as cur:
                await cur.execute(query1, (notebook_id, user_id))
                notebook = await cur.fetchone()
                if not notebook:
                    raise HTTPException(status_code=401, detail="No access to delete message history")
                
                await cur.execute(query2, (notebook_id,))
                await connector.commit()
        except Error as err:
            await connector.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to delete message history: {err.msg}")
        finally:
            await connector.close()

    async def add_message_to_history(self, notebook_id: str, user_id: str, message: str, is_from_user: bool = False):
        connector = await get_mysql_connection()
        try:
            query1 = "SELECT notebook_id FROM notebook WHERE notebook_id = %s and user_id = %s"
            query2 = "INSERT INTO messages (message_id, notebook_id, content) VALUES (%s, %s, %s)"
            async with await connector.cursor() as cur:
                message_id = f"a-{uuid.uuid4()}" if is_from_user else f"b-{uuid.uuid4()}"
                await cur.execute(query1, (notebook_id, user_id))
                notebook = await cur.fetchone()
                if not notebook:
                    raise HTTPException(status_code=401, detail="No access to add message to history")
                
                await cur.execute(query2, (message_id, notebook_id, message))
                await connector.commit()
        except Error as err:
            await connector.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to add message to history: {err.msg}")
        finally:
            await connector.close()

    async def get_top_recent_notebooks_by_user_id(self, user_id) -> list[BaseNotebook]:
        connector = await get_mysql_connection()
        try:
            query = "SELECT * FROM notebook WHERE user_id = %s ORDER BY last_access_at desc LIMIT 4"

            async with await connector.cursor() as cur:
                await cur.execute(query, (user_id,))
                rows = await cur.fetchall()
                results = [
                    BaseNotebook(
                        notebook_id=row[0],
                        user_id=row[1],
                        title=row[2],
                        created_at=row[3],
                        last_access_at=row[4],
                    )
                    for row in rows
                ]
                return results
        except Error as err:
            raise HTTPException(status_code=400, detail=f"Failed to get notebooks: {err.msg}")
        finally:
            await connector.close()

    async def submit_message(self, notebook_id: str, user_id: str, message: str, file_ids: list[str]):
        try:
            chat_agent = RagAgent(file_ids)

            message_history = await self.get_all_messages(notebook_id, user_id)
            answer = chat_agent.get_answer(message, message_history)
            await self.add_message_to_history(notebook_id, user_id, message, is_from_user=True)
            await self.add_message_to_history(notebook_id, user_id, answer)
            return answer
        except Error as err:
            raise HTTPException(status_code=400, detail=f"Failed to submit message: {err.msg}")
        

    async def get_all_messages(self, notebook_id: str, user_id: str):
        connector = await get_mysql_connection()
        try:
            query1 = "SELECT notebook_id FROM notebook WHERE notebook_id = %s and user_id = %s"
            query2 = "SELECT * FROM messages WHERE notebook_id = %s order by created_at"
            async with await connector.cursor() as cur:
                await cur.execute(query1, (notebook_id, user_id))
                notebook = await cur.fetchone()
                if not notebook:
                    raise HTTPException(status_code=401, detail="No access to get messages")
                
                await cur.execute(query2, (notebook_id,))
                rows = await cur.fetchall()
                results = [
                    BaseMessage(
                        message_id=row[0],
                        notebook_id=row[1],
                        content=row[2],
                        created_at=row[3],
                    )
                    for row in rows
                ]
                return results
        except Error as err:
            raise HTTPException(status_code=400, detail=f"Failed to get messages: {err.msg}")
        finally:
            await connector.close()


    async def get_all_files(self, notebook_id: str, user_id: str) -> list[BaseFile]:
        connector = await get_mysql_connection()
        try:
            query1 = "SELECT notebook_id FROM notebook WHERE notebook_id = %s and user_id = %s"
            query2 = "SELECT * FROM file WHERE notebook_id = %s"
            async with await connector.cursor() as cur:
                await cur.execute(query1, (notebook_id, user_id))
                notebook = await cur.fetchone()
                if not notebook:
                    raise HTTPException(status_code=401, detail="No access to get files")
                
                await cur.execute(query2, (notebook_id,))
                rows = await cur.fetchall()
                results = [
                    BaseFile(
                        file_id=row[0],
                        notebook_id=row[1],
                        file_name=row[2],
                        extensions=row[3],
                        upload_at=row[4],
                        file_path=row[5]
                    )
                    for row in rows
                ]
                return results
        except Error as err:
            raise HTTPException(status_code=400, detail=f"Failed to get files: {err.msg}")