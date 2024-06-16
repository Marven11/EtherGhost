from enum import Enum
from uuid import UUID, uuid4
import typing as t
from pydantic import BaseModel, model_validator, Field, validator

__all__ = [
    "SessionInfo",
    "SessionConnOnelinePHP",
    "session_type_readable"
]


class SessionConnOnelinePHP(BaseModel):
    """PHP一句话webshell的连接信息"""

    url: str
    password: str
    method: str
    http_params_obfs: bool
    encoder: t.Literal["raw", "base64"] = "raw"
    sessionize_payload: bool = True


class SessionConnBehinderPHPAES(BaseModel):
    """冰蝎PHP AES的连接信息"""

    url: str
    password: str
    encoder: t.Literal["raw", "base64"] = "raw"
    sessionize_payload: bool = True

class SessionConnBehinderPHPXor(BaseModel):
    """冰蝎PHP Xor的连接信息"""

    url: str
    password: str
    encoder: t.Literal["raw", "base64"] = "raw"
    sessionize_payload: bool = True

SessionConnectionInfo = t.Union[
    SessionConnOnelinePHP,
    SessionConnBehinderPHPAES,
    SessionConnBehinderPHPXor,
]


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
