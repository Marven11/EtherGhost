"""管理session相关的函数，实现了session info的CRUD与session的实例化等"""

import typing as t
from uuid import UUID
from . import db, core
from .core.base import session_type_info
from .session_types import (
    SessionInfo,
)


location_readable = {"US": "🇺🇸"}
session_con_converters = {}


def session_info_to_session(session_info: SessionInfo) -> core.SessionInterface:
    """将session info转成session对象

    Args:
        session_info (SessionInfo): session info

    Returns:
        session.Session: session对象
    """
    # TODO: make it tolerant, when session type not found the program shouldn't break
    # instead, it should tell user that it cannot find the session type
    if session_info.session_type not in session_type_info:
        raise ValueError(f"Session type {session_info.session_type} is not supported!")
    constructor = session_type_info[session_info.session_type]["constructor"]
    return constructor(session_info.connection)


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


def get_session_by_id(
    session_id: t.Union[str, UUID]
) -> core.SessionInterface:
    """根据id返回session对象，优先返回缓存的对象

    Args:
        session_id (t.Union[str, UUID]): session id

    Returns:
        t.Union[None, session.Session]: session对象，找不到时返回None
    """
    if isinstance(session_id, str):
        session_id = UUID(session_id)
    session_info = get_session_info_by_id(session_id)
    if session_info is None:
        raise core.UserError("没有这个UUID对应的Session!")
    return session_info_to_session(session_info)


def list_sessions_readable() -> t.List[t.Dict[str, t.Any]]:
    """列出所有的session info

    Returns:
        t.List[SessionInfo]: 所有的session info
    """
    results = []
    for sess in db.list_sessions():
        results.append(
            {
                "type": sess.session_type,
                "readable_type": session_type_info[sess.session_type]["readable_name"],
                "id": sess.session_id,
                "name": sess.name,
                "note": sess.note,
                "location": location_readable.get(sess.location, "未知位置"),
            }
        )
    return results


def add_session_info(info: SessionInfo):
    """将session info添加到数据库"""
    db.add_session_info(info)


def delete_session_info_by_id(session_id: UUID):
    """根据session id删除某个session"""
    db.delete_session_info_by_id(session_id)
