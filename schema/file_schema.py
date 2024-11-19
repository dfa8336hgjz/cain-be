from typing import *
from abc import ABC
from datetime import datetime
from pydantic import BaseModel

class BaseFile(BaseModel):
    file_id: str
    notebook_id: str
    file_name: str
    extensions: Literal['pdf', 'docx']
    upload_at: datetime = datetime.now()
    file_path: str