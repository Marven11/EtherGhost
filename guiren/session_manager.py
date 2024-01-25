import typing as t
from uuid import UUID
from . import db, sessions
from .session_types import (
    SessionType,
    SessionInfo,
    SessionConnOnelinePHP,
)


session_type_readable = {SessionType.ONELINE_PHP: "PHP一句话"}
location_readable = {"US": "🇺🇸"}
sessions_obj = {}
session_con_converters = {}


def session_conn_converter(session_type):
    """标记将session info转换为session对象的函数"""

    def _wrapper(f):
        session_con_converters[session_type] = f
        return f

    return _wrapper


@session_conn_converter(SessionType.ONELINE_PHP)
def php_normal(session_conn: SessionConnOnelinePHP):
    """将PHP一句话的info转换成对象"""
    return sessions.PHPWebshellOneliner(
        method=session_conn.method,
        url=session_conn.url,
        password=session_conn.password,
        options=sessions.php.PHPWebshellOptions(
            encoder=session_conn.encoder,
            http_params_obfs=session_conn.http_params_obfs
        )
    )
    # return session.PHPWebshellNormal(
    #     method=session_conn.method,
    #     url=session_conn.url,
    #     password=session_conn.password,
    # )


def session_info_to_session(session_info: SessionInfo) -> sessions.Session:
    """将session info转成session对象

    Args:
        session_info (SessionInfo): session info

    Returns:
        session.Session: session对象
    """
    f = session_con_converters[session_info.session_type]
    return f(session_info.connection)


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
    return db.get_session_info_by_id(session_id)


def get_session_by_id(session_id: t.Union[str, UUID]) -> t.Union[None, sessions.Session]:
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
    for sess in db.list_sessions():
        results.append(
            {
                "type": session_type_readable.get(sess.session_type, "未知类型"),
                "id": sess.session_id,
                "name": sess.name,
                "note": sess.note,
                "location": location_readable.get(sess.location, "未知位置"),
            }
        )
    return results

def add_session_info(info: SessionInfo):
    db.add_session_info(info)

def delete_session_info_by_id(session_id: UUID):
    db.delete_session_info_by_id(session_id)
    if session_id in sessions_obj:
        del sessions_obj[session_id]
