
from typing import List
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