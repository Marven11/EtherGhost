import typing as t
from session import session
from enum import Enum
from typing import TypedDict
from uuid import uuid4, UUID


class SessionType(Enum):
    ONELINE_PHP = "ONELINE_PHP"


class SessionInfo(TypedDict):
    session_type: SessionType
    session_id: UUID
    name: str
    note: str
    location: str


class SessionInfoNormalPHP(SessionInfo):
    method: str
    url: str
    password: str


session_type_readable = {SessionType.ONELINE_PHP: "PHP一句话"}

location_readable = {"US": "🇺🇸"}
sessions_obj = {}
session_info_converters = {}
T = t.TypeVar("T", bound=SessionType)


def session_info_converter(session_type):
    def _wrapper(f):
        session_info_converters[session_type] = f
        return f

    return _wrapper


@session_info_converter(SessionType.ONELINE_PHP)
def php_normal(session_info: T):
    return session.PHPWebshellNormal(
        method=session_info["method"],
        url=session_info["url"],
        password=session_info["password"],
    )


def session_info_to_session(session_info: T):
    f = session_info_converters[session_info["session_type"]]
    return f(session_info)


def get_session_by_id(session_id: t.Union[str, UUID]):
    if isinstance(session_id, str):
        session_id = UUID(session_id)
    if session_id not in sessions_obj:
        session_info = [
            session_info
            for session_info in sessions_info
            if session_info["session_id"] == session_id
        ]
        if not session_info:
            return None
        session_info = session_info[0]
        sessions_obj[session_id] = session_info_to_session(session_info)

    return sessions_obj[session_id]


def list_sessions_readable():
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
    SessionInfoNormalPHP(
        method="POST",
        url="http://127.0.0.1:8081/shell.php",
        password="data",
        name="本地webshell",
        session_type=SessionType.ONELINE_PHP,
        session_id=uuid4(),
        note="",
        location="US",
    ),
    SessionInfoNormalPHP(
        method="POST",
        url="http://127.0.0.1:8081/shell.php",
        password="data",
        name="另一个webshell",
        session_type=SessionType.ONELINE_PHP,
        session_id=uuid4(),
        note="",
        location="US",
    ),
    SessionInfoNormalPHP(
        method="POST",
        url="http://127.0.0.1:8081/shell.php",
        password="data",
        name="又一个webshell",
        session_type=SessionType.ONELINE_PHP,
        session_id=uuid4(),
        note="",
        location="US",
    ),
    SessionInfoNormalPHP(
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

