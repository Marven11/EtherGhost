from enum import Enum
from dataclasses import dataclass
from uuid import UUID

__all__ = [
    "SessionType",
    "SessionConnectionInfo",
    "SessionInfo",
    "SessionConnOnelinePHP",
]


class SessionType(Enum):
    """session的类型"""

    ONELINE_PHP = "ONELINE_PHP"


@dataclass
class SessionConnectionInfo:
    """session的连接信息"""


@dataclass
class SessionInfo:
    """session的基本信息"""

    session_type: SessionType
    session_id: UUID
    name: str
    connection: SessionConnectionInfo
    note: str = ""
    location: str = ""


# 各个session的连接信息


@dataclass
class SessionConnOnelinePHP(SessionConnectionInfo):
    """PHP一句话webshell的连接信息"""

    url: str
    password: str
    method: str = "POST"
