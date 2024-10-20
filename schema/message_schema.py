from typing import Optional
from abc import ABC
from datetime import datetime
from pydantic import BaseModel

class BaseMessage(BaseModel):
    message_id: str
    created_at: datetime = datetime.now()
    content: Optional[str] = None
    conversation_id: Optional[str] = None
