from db.mysql_db import get_mysql_connection
from mysql.connector import Error
from fastapi import HTTPException
from schema.user_schema import BaseUser

class UserController:
    def __init__(self):
        pass

    async def get_user_info(self, user_id):
        connector = await get_mysql_connection()
        try:
            query = "SELECT * FROM user WHERE user_id = %s"
            async with await connector.cursor() as cur:
                await cur.execute(query, (user_id,))
                user = await cur.fetchone()
                if user:
                    return BaseUser(
                        user_id=user[0],
                        username=user[1],
                        email=user[2],
                        fullname=user[3],
                        password=user[4],
                        created_at=user[5],
                    )

        except Error as err:
            raise HTTPException(status_code=400, detail=f"Failed to get user: {err.msg}")

    async def delete_user_by_id(self, user_id):
        connector = await get_mysql_connection()
        try:
            query = "DELETE FROM user WHERE user_id = %s"
            async with await connector.cursor() as cur:
                await cur.execute(query, (user_id,))
                await connector.commit()
        except Error as err:
            await connector.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to delete user: {err.msg}")