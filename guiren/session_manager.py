"""管理session相关的函数，实现了session info的CRUD与session的实例化等"""

import typing as t
from uuid import UUID
from . import db, sessions
from .session_types import (
    SessionType,
    SessionInfo,
    SessionConnOnelinePHP,
    SessionConnBehinderPHPAES,
    SessionConnBehinderPHPXor,
)


session_type_readable = {
    SessionType.ONELINE_PHP: "PHP一句话",
    SessionType.BEHINDER_PHP_AES: "冰蝎PHP AES",
    SessionType.BEHINDER_PHP_XOR: "冰蝎PHP Xor",
}
location_readable = {"US": "🇺🇸"}
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
        http_params_obfs=session_conn.http_params_obfs,
        options=sessions.php.PHPWebshellOptions(
            encoder=session_conn.encoder,
        ),
    )


@session_conn_converter(SessionType.BEHINDER_PHP_AES)
def php_behinderaes(session_conn: SessionConnBehinderPHPAES):
    """将冰蝎PHP AES的info转换成对象"""
    return sessions.PHPWebshellBehinderAES(
        url=session_conn.url,
        password=session_conn.password,
        options=sessions.php.PHPWebshellOptions(
            encoder=session_conn.encoder,
        ),
    )


@session_conn_converter(SessionType.BEHINDER_PHP_XOR)
def php_behinderxor(session_conn: SessionConnBehinderPHPXor):
    """将冰蝎PHP Xor的info转换成对象"""
    return sessions.PHPWebshellBehinderXor(
        url=session_conn.url,
        password=session_conn.password,
        options=sessions.php.PHPWebshellOptions(
            encoder=session_conn.encoder,
        ),
    )


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


def get_session_by_id(
    session_id: t.Union[str, UUID]
) -> t.Union[None, sessions.Session]:
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
        return None
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
                "type": session_type_readable.get(sess.session_type, "未知类型"),
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
