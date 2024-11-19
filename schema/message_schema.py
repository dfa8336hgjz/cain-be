from typing import Optional
from abc import ABC
from datetime import datetime
from pydantic import BaseModel

class BaseMessage(BaseModel):
    message_id: str
    notebook_id: str
    content: Optional[str] = None
    created_at: datetime = datetime.now()
