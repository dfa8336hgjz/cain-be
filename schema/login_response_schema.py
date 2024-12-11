from pydantic import BaseModel

class BaseUserInfo(BaseModel):
    user_id: str
    username: str
    email: str
    fullname: str
    token: str = None