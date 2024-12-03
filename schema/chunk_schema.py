from typing import *
from abc import ABC
from datetime import datetime
from pydantic import BaseModel


class BaseChunk(BaseModel):
    chunk_id: str
    content: str
    file_id: str
    notebook_id: str