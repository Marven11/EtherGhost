"""
Session统一管理模块

负责管理两种核心对象：
1. SessionInfo - 存储session的元数据(名称、备注)和连接配置
2. Session - 实现SessionInterface的实际操作对象，由SessionInfo构造

主要功能：
- SessionInfo的CRUD操作
- Session对象的缓存和生命周期管理
- 两种对象的转换
"""

import time
import typing as t
from uuid import UUID

from .utils import db
from . import core, session_connector
from .core.base import session_type_info
from .session_types import (
    SessionInfo,
)

SESSION_CACHE_TIMEOUT = 300
session_store: t.Dict[UUID, t.Tuple[int, core.SessionInterface]] = {}
location_readable = {"US": "🇺🇸"}


def session_info_to_session(session_info: SessionInfo) -> core.SessionInterface:
    """将session info转成session对象

    Args:
        session_info (SessionInfo): session info

    Returns:
        session.Session: session对象
    """
    if session_info.session_type not in session_type_info:
        raise core.UserError(f"Session类型{session_info.session_type}不存在")
    constructor = session_type_info[session_info.session_type]["constructor"]
    return constructor(session_info.connection)


def get_session_info_by_id(
    session_id: t.Union[str, UUID],
) -> t.Union[None, SessionInfo]:
    """根据id返回session info

    Args:
        session_id (t.Union[str, UUID]): session id

    Returns:
        t.Union[None, SessionInfo]: session info，找不到时返回None
    """
    if isinstance(session_id, str):
        session_id = UUID(session_id)
    result = db.get_session_info_by_id(session_id)
    if result is not None:
        return result
    return session_connector.get_session(session_id)


def get_session_by_id(session_id: t.Union[str, UUID]) -> core.SessionInterface:
    """根据id返回session对象，优先返回缓存的对象

    Args:
        session_id (t.Union[str, UUID]): session id

    Returns:
        t.Union[None, session.Session]: session对象，找不到时返回None
    """
    if isinstance(session_id, str):
        session_id = UUID(session_id)
    cache_timeout_sessions = [
        uuid
        for uuid, (timestamp, _) in session_store.items()
        if timestamp + SESSION_CACHE_TIMEOUT < time.time()
    ]
    for uuid in cache_timeout_sessions:
        del session_store[uuid]
    if session_id in session_store:
        _, session = session_store[session_id]
        session_store[session_id] = (int(time.time()), session)
        return session

    session_info = get_session_info_by_id(session_id)
    if session_info is None:
        raise core.UserError("没有这个UUID对应的Session!")
    session = session_info_to_session(session_info)
    session_store[session_id] = (int(time.time()), session)
    return session


def clear_session_cache():
    session_store.clear()


def session_to_readable(sess: SessionInfo) -> t.Dict[str, t.Any]:
    """将SessionInfo对象转换为可读的字典"""
    return {
        "type": sess.session_type,
        "readable_type": session_type_info[sess.session_type]["readable_name"],
        "id": sess.session_id,
        "name": sess.name,
        "note": sess.note,
        "location": location_readable.get(sess.location, "未知位置"),
    }


def list_sessions_db_readable() -> t.List[t.Dict[str, t.Any]]:
    """列出所有的session info（可读格式）"""
    return [session_to_readable(sess) for sess in db.list_sessions()]


def add_session_info(info: SessionInfo):
    """将session info添加到数据库"""
    db.add_session_info(info)


def delete_session_info_by_id(session_id: UUID):
    """根据session id删除某个session"""
    db.delete_session_info_by_id(session_id)
