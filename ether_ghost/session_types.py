from uuid import UUID, uuid4
import typing as t
from pydantic import BaseModel, Field

class SessionInfo(BaseModel):
    """session的基本信息"""

    session_type: str
    name: str
    connection: t.Dict[str, t.Any]
    session_id: UUID = Field(default_factory=uuid4)
    note: str = ""
    location: str = ""

    class Config:
        from_attributes = True
