from enum import Enum
from uuid import UUID, uuid4
import typing as t
from pydantic import BaseModel, model_validator, Field, validator

__all__ = [
    "SessionType",
    "SessionConnectionInfo",
    "SessionInfo",
    "SessionConnOnelinePHP",
    "type_to_class",
]


class SessionType(Enum):
    """session的类型"""

    ONELINE_PHP = "ONELINE_PHP"
    BEHINDER_PHP_AES = "BEHINDER_PHP_AES"
    BEHINDER_PHP_XOR = "BEHINDER_PHP_XOR"


# 各个session的连接信息
class SessionConnectionInfoBase(BaseModel):
    """session的连接信息"""


class SessionConnOnelinePHP(SessionConnectionInfoBase):
    """PHP一句话webshell的连接信息"""

    url: str
    password: str
    method: str
    http_params_obfs: bool
    encoder: t.Literal["raw", "base64"] = "raw"


class SessionConnBehinderPHPAES(SessionConnectionInfoBase):
    """PHP一句话webshell的连接信息"""

    url: str
    password: str
    encoder: t.Literal["raw", "base64"] = "raw"

class SessionConnBehinderPHPXor(SessionConnectionInfoBase):
    """冰蝎PHP Xor的连接信息"""

    url: str
    password: str
    encoder: t.Literal["raw", "base64"] = "raw"


SessionConnectionInfo = t.Union[SessionConnOnelinePHP, SessionConnBehinderPHPAES, SessionConnBehinderPHPXor]


class SessionInfo(BaseModel):
    """session的基本信息"""

    session_type: SessionType
    name: str
    connection: SessionConnectionInfo
    session_id: UUID = Field(default_factory=uuid4)
    note: str = ""
    location: str = ""

    # 使用validator装饰器来实现动态类型
    @validator("connection", pre=True, always=True)
    @classmethod
    def set_dynamic_attr_type(cls, v, values):  # type: ignore
        session_type = values.get("session_type")
        conn_class = type_to_class[SessionType(session_type)]
        if isinstance(v, dict):
            result = conn_class(**v)
            return result
        elif isinstance(v, conn_class):
            return v
        raise NotImplementedError(
            f"Serialization from type {type(v)} is not supported."
        )

    @model_validator(mode="after")
    def validator(self):
        conn_class = type_to_class[self.session_type]
        if not isinstance(self.connection, conn_class):
            raise ValueError(f"Wrong connection data for {self.session_type}")
        return self

    class Config:
        from_attributes = True


type_to_class = {
    SessionType.ONELINE_PHP: SessionConnOnelinePHP,
    SessionType.BEHINDER_PHP_AES: SessionConnBehinderPHPAES,
    SessionType.BEHINDER_PHP_XOR: SessionConnBehinderPHPXor,
}
