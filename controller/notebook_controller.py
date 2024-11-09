from typing import List
import uuid
from db.mysql_db import get_mysql_connection
from mysql.connector import Error
from fastapi import HTTPException

from schema.notebook_schema import BaseNotebook

class NotebookController:
    async def get_all_notebooks_by_user_id(self, user_id) -> List[BaseNotebook]:
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
            raise HTTPException(status_code=400, detail=f"Failed to get notebooks: {err.msg} ")
        
    async def create_notebook_by_user_id(self, user_id, title):
        connector = await get_mysql_connection()
        notebook_id = f"notebook-{uuid.uuid4()}"
        try:
            query1 = "SELECT notebook_id FROM notebook WHERE title = %s and user_id = %s"
            query2 = "INSERT INTO notebook (notebook_id, user_id, title) VALUES (%s, %s, %s)"

            async with await connector.cursor() as cur:
                await cur.execute(query1, (title, user_id))
                notebook = await cur.fetchone()
                if notebook:
                    raise HTTPException(status_code=401, detail="Notebook already exists")
                
                await cur.execute(query2, (notebook_id, user_id, title if title else "Untitled notebook"))
                await connector.commit()
                return notebook_id
        except Error as err:
            connector.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to create notebook: {err.msg}")
        
    async def delete_notebook_by_id(self, notebook_id, user_id):
        connector = await get_mysql_connection()
        try:
            query = "DELETE FROM notebook WHERE notebook_id = %s and user_id = %s"
            async with await connector.cursor() as cur:
                await cur.execute(query, (notebook_id, user_id))
                await connector.commit()
        except Error as err:
            await connector.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to delete notebook: {err.msg}")
        
    async def get_notebook_by_id(self, notebook_id, user_id):
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
        
    async def update_notebook_access_time(self, notebook_id, user_id):
        connector = await get_mysql_connection()
        try:
            query = "UPDATE notebook SET last_access_at = NOW() WHERE notebook_id = %s and user_id = %s"
            async with await connector.cursor() as cur:
                await cur.execute(query, (notebook_id, user_id))
                await connector.commit()
        except Error as err:
            await connector.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to update notebook access time: {err.msg}")
        
    async def delete_message_history(self, notebook_id, user_id):
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
        
    async def add_message_to_history(self, notebook_id, user_id, message, is_from_user):
        connector = await get_mysql_connection()
        try:
            query1 = "SELECT notebook_id FROM notebook WHERE notebook_id = %s and user_id = %s"
            query2 = "INSERT INTO messages (notebook_id, content, is_from_user) VALUES (%s, %s, %s, %s)"
            async with await connector.cursor() as cur:
                await cur.execute(query1, (notebook_id, user_id))
                notebook = await cur.fetchone()
                if not notebook:
                    raise HTTPException(status_code=401, detail="No access to add message to history")
                
                await cur.execute(query2, (notebook_id, message, is_from_user))
                await connector.commit()
        except Error as err:
            await connector.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to add message to history: {err.msg}")