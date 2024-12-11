from datetime import datetime, timedelta
import uuid

from db.mysql_db import get_mysql_connection
from mysql.connector import Error
import mysql.connector.aio
from typing import Any, Union
from passlib.context import CryptContext

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from pydantic import ValidationError
import jwt
from db.redis_db import RedisService
from schema.login_response_schema import BaseUserInfo


SECURITY_ALGORITHM = 'HS256'
SECRET_KEY = '123456'

reusable_oauth2 = HTTPBearer(
    scheme_name='Authorization'
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthController:
    def __init__(self, app_controller):
        self.controller = app_controller
        
    async def verify_password(self, username, password) -> BaseUserInfo:
        try:
            connector = await get_mysql_connection()

            query = "SELECT * FROM user WHERE username = %s"
            async with await connector.cursor() as cur:
                await cur.execute(query, (username,))
                user = await cur.fetchone()
                if user and pwd_context.verify(password, user[4]):
                    return BaseUserInfo(
                        user_id=user[0],
                        username=user[1],
                        email=user[2],
                        fullname=user[3]
                    )
                return None
        except Error as err:
            raise HTTPException(status_code=400, detail=err.msg)
        finally:
            await connector.close()
    
    def generate_token(self, user_id: str) -> str:
        expire = datetime.now() + timedelta(
            seconds = 60 * 60 * 24 * 3
        )
        to_encode = {
            "exp": expire, "id": user_id
        }
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=SECURITY_ALGORITHM)
        return encoded_jwt
    
    async def create_user(self, username, password, email, fullname):
        hashed_password = pwd_context.hash(password)
        user_id = f"user-{uuid.uuid4()}"
        connector = await get_mysql_connection()
        try:
            query1 = "SELECT * FROM user WHERE username = %s"
            query2 = "INSERT INTO user (user_id, username, password, email, fullname) VALUES (%s, %s, %s, %s, %s)"

            async with await connector.cursor() as cur:
                await cur.execute(query1, (username,))
                user = await cur.fetchone()
                if user:
                    raise HTTPException(status_code=450, detail="User already exists")
                
                await cur.execute(query2, (user_id, username, hashed_password, email, fullname))
                await connector.commit()
                return
        except mysql.connector.Error as err:
            connector.rollback()
            raise HTTPException(status_code=400, detail=err.msg)
        finally:
            await connector.close()

    async def save_token_to_blacklist(self, token: str, redis_client: RedisService = Depends(RedisService)):
        await redis_client.add_token_to_blacklist(token)

def validate_token(http_authorization_credentials=Depends(reusable_oauth2)):
    try:
        token = http_authorization_credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[SECURITY_ALGORITHM])
        if payload.get('exp') < datetime.now().timestamp():
            raise HTTPException(status_code=403, detail="Token expired")

        return payload.get('id')
    except(jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=403,
            detail=f"Could not validate credentials",
        )