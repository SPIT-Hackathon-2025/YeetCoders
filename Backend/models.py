from pydantic import BaseModel
from typing import Optional

class Email(BaseModel):
    sender: str
    subject: str
    message_id: str