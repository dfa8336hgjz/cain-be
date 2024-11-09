from pydantic import BaseModel
from datetime import datetime

class BaseUser(BaseModel):
    user_id: str
    username: str
    email: str
    fullname: str
    password: str
    created_at: datetime