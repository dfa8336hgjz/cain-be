from typing import *
from abc import ABC
from datetime import datetime
from pydantic import BaseModel


class BaseChunk(BaseModel):
    chunk_id: str
    content: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    document_id: str
    order_in_ref: int = -1