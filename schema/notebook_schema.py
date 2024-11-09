from datetime import datetime
from pydantic import BaseModel

class BaseNotebook(BaseModel):
    notebook_id: str
    user_id: str
    title: str
    created_at: datetime
    last_access_at: datetime