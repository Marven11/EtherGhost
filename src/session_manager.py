import typing as t
from enum import Enum
from typing import TypedDict
from uuid import uuid4, UUID
from session import session


class SessionType(Enum):
    """session的类型"""

    ONELINE_PHP = "ONELINE_PHP"


class SessionInfo(TypedDict):
    """session的基本信息"""

    session_type: SessionType
    session_id: UUID
    name: str
    note: str
    location: str


class SessionInfoOnelinePHP(SessionInfo):
    """PHP一句话webshell的信息"""

    method: str
    url: str
    password: str


session_type_readable = {SessionType.ONELINE_PHP: "PHP一句话"}

location_readable = {"US": "🇺🇸"}
sessions_obj = {}
session_info_converters = {}
T = t.TypeVar("T", bound=SessionType)


def session_info_converter(session_type):
    """标记将session info转换为session对象的函数"""

    def _wrapper(f):
        session_info_converters[session_type] = f
        return f

    return _wrapper


@session_info_converter(SessionType.ONELINE_PHP)
def php_normal(session_info: T):
    """将PHP一句话的info转换成对象"""
    return session.PHPWebshellNormal(
        method=session_info["method"],
        url=session_info["url"],
        password=session_info["password"],
    )


def session_info_to_session(session_info: T) -> session.Session:
    """将session info转成session对象

    Args:
        session_info (SessionInfo): session info

    Returns:
        session.Session: session对象
    """
    f = session_info_converters[session_info["session_type"]]
    return f(session_info)


def get_session_info_by_id(
    session_id: t.Union[str, UUID]
) -> t.Union[None, SessionInfo]:
    """根据id返回session info

    Args:
        session_id (t.Union[str, UUID]): session id

    Returns:
        t.Union[None, SessionInfo]: session info，找不到时返回None
    """
    if isinstance(session_id, str):
        session_id = UUID(session_id)
    session_infos = [
        session_info
        for session_info in sessions_info
        if session_info["session_id"] == session_id
    ]
    if not session_infos:
        return None
    return session_infos[0]


def get_session_by_id(session_id: t.Union[str, UUID]) -> t.Union[None, session.Session]:
    """根据id返回session对象，优先返回缓存的对象

    Args:
        session_id (t.Union[str, UUID]): session id

    Returns:
        t.Union[None, session.Session]: session对象，找不到时返回None
    """
    if isinstance(session_id, str):
        session_id = UUID(session_id)
    if session_id not in sessions_obj:
        session_info = get_session_info_by_id(session_id)
        if session_info is None:
            return None
        sessions_obj[session_id] = session_info_to_session(session_info)

    return sessions_obj[session_id]


def list_sessions_readable() -> t.List[SessionInfo]:
    """列出所有的session info

    Returns:
        t.List[SessionInfo]: 所有的session info
    """
    results = []
    for sess in sessions_info:
        results.append(
            {
                "type": session_type_readable.get(sess["session_type"], "未知类型"),
                "id": sess["session_id"],
                "name": sess["name"],
                "note": sess["note"],
                "location": location_readable.get(sess["location"], "未知位置"),
            }
        )
    return results


sessions_info = [
    SessionInfoOnelinePHP(
        method="POST",
        url="http://127.0.0.1:8081/shell.php",
        password="data",
        name="本地webshell",
        session_type=SessionType.ONELINE_PHP,
        session_id=uuid4(),
        note="",
        location="US",
    ),
    SessionInfoOnelinePHP(
        method="POST",
        url="http://127.0.0.1:8081/shell.php",
        password="data",
        name="另一个webshell",
        session_type=SessionType.ONELINE_PHP,
        session_id=uuid4(),
        note="",
        location="US",
    ),
    SessionInfoOnelinePHP(
        method="POST",
        url="http://127.0.0.1:8081/shell.php",
        password="data",
        name="又一个webshell",
        session_type=SessionType.ONELINE_PHP,
        session_id=uuid4(),
        note="",
        location="US",
    ),
    SessionInfoOnelinePHP(
        method="POST",
        url="http://127.0.0.1:8081/shell.php",
        password="data",
        name="还是一个webshell",
        session_type=SessionType.ONELINE_PHP,
        session_id=uuid4(),
        note="",
        location="US",
    ),
]


if __name__ == "__main__":
    uuid = sessions_info[0]["session_id"]
    print(UUID(str(uuid)) == uuid)
