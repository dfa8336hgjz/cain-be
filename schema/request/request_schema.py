
from typing import List
from fastapi import UploadFile
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str

class SignupRequest(BaseModel):
    username: str
    password: str
    email: str
    fullname: str
    
class MessageRequest(BaseModel):
    message: str
    file_id: list[str]
    notebook_id: str

class NotebookRenameRequest(BaseModel):
    notebook_id: str
    title: str
