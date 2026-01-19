import asyncio
import logging
import uuid
from typing import ClassVar, Protocol, Dict, Any

from .utils import db
from .core import exceptions
from .core.base import SessionInterface, OptionGroup, session_type_info
from .session_types import SessionInfo

logger = logging.getLogger("core.session_connector")


# 基类定义
class SessionConnector(Protocol):
    connector_name: ClassVar[str]
    connector_name_readable: ClassVar[str]
    session_class: ClassVar[type[SessionInterface]]
    options: ClassVar[list[OptionGroup]]

    def __init__(self, connector_id: uuid.UUID, config: dict):
        raise NotImplementedError()

    async def run(self):
        raise NotImplementedError()

    def get_session_type(self) -> str:
        raise NotImplementedError()

    def build_session(self, config: dict) -> SessionInterface:
        raise NotImplementedError()

    async def close_session(self, config: dict):
        raise NotImplementedError()


class DirectSessionConnector(SessionConnector):
    connector_name: ClassVar[str]
    connector_name_readable: ClassVar[str]
    session_class: ClassVar[type[SessionInterface]]
    options: ClassVar[list[OptionGroup]]

    def __init__(self, connector_id: uuid.UUID, config: dict):
        self.config = config
        self.connector_id = connector_id

    async def run(self) -> None:
        pass

    def get_session_type(self) -> str:
        raise NotImplementedError()

    def build_session(self, config: dict) -> SessionInterface:
        raise NotImplementedError()

    async def close_session(self, config: dict):
        pass


# 全局变量（在基类定义之后）
connector_sessions: dict[uuid.UUID, SessionInfo] = {}
session_connectors: dict[str, type[SessionConnector]] = {}
started_connectors: dict[uuid.UUID, tuple[SessionConnector, asyncio.Task]] = {}
_direct_connector_registry: Dict[str, str] = {}
_direct_connector_instances: dict[str, SessionConnector] = {}


# 注册函数
def register_direct_connector(cls):
    """装饰器，用于注册手动定义的直接型connector类"""
    session_type = cls.session_class.session_type
    session_connectors[cls.connector_name] = cls
    _direct_connector_registry[session_type] = cls.connector_name

    virtual_connector_id = uuid.uuid5(uuid.NAMESPACE_DNS, cls.connector_name)
    default_instance = cls(virtual_connector_id, {})
    _direct_connector_instances[cls.connector_name] = default_instance

    if session_type in session_type_info:
        raise RuntimeError(f"Session type {session_type} already registered in session_type_info")
    session_type_info[session_type] = {
        "constructor": cls.session_class,
        "options": cls.session_class.conn_options,
        "readable_name": cls.session_class.readable_name,
        "session_class": cls.session_class,
    }

    return cls


def register_connector(clazz: type[SessionConnector]):
    """注册connector类"""
    session_connectors[clazz.connector_name] = clazz
    return clazz


# 会话管理函数
def get_session(client_id: uuid.UUID):
    return connector_sessions.get(client_id, None)


def list_sessions():
    return list(connector_sessions.values())


def register_session(client_id: uuid.UUID, session_info: SessionInfo):
    connector_sessions[client_id] = session_info


def delete_session(client_id: uuid.UUID):
    del connector_sessions[client_id]


# 连接器查找函数
def get_connector_of_session(client_id: uuid.UUID):
    session = get_session(client_id)
    if not session:
        return None
    for connector, _ in started_connectors.values():
        if connector.get_session_type() == session.session_type:
            return connector
    return None


def get_connector_for_session_type(session_type: str) -> type[SessionConnector] | None:
    if session_type in _direct_connector_registry:
        connector_name = _direct_connector_registry[session_type]
        return session_connectors.get(connector_name)

    for connector, _ in started_connectors.values():
        if connector.get_session_type() == session_type:
            for connector_cls in session_connectors.values():
                if connector_cls.connector_name == connector.connector_name:
                    return connector_cls

    return None


def get_connector_instance_by_session_type(
    session_type: str,
) -> SessionConnector | None:
    if session_type in _direct_connector_instances:
        return _direct_connector_instances[session_type]

    for connector, _ in started_connectors.values():
        if connector.get_session_type() == session_type:
            return connector

    return None


# 连接器生命周期管理
async def start_connector(connector_id: uuid.UUID):
    if connector_id in started_connectors:
        raise exceptions.UserError(f"Connector {connector_id} 已经启动")

    connector_info = db.get_session_connector_by_connector_id(connector_id)
    if connector_info is None:
        raise RuntimeError(f"找不到connector {connector_id}")

    clazz = session_connectors[connector_info.connector_type]
    logger.debug(f"Connector info: {connector_info.connection=}")
    connector = clazz(connector_id, connector_info.connection)
    task = asyncio.create_task(connector.run())

    started_connectors[connector_id] = (connector, task)

    session_type = connector.get_session_type()
    session_type_info[session_type] = {
        "constructor": connector.build_session,
        "options": clazz.session_class.conn_options,
        "readable_name": f"{connector_info.name} {clazz.session_class.readable_name}",
        "session_class": clazz.session_class,
    }

    return task


async def stop_connector(connector_id: uuid.UUID):
    if connector_id not in started_connectors:
        raise exceptions.UserError(f"Connector {connector_id} 未启动")

    connector_info = db.get_session_connector_by_connector_id(connector_id)
    if connector_info is None:
        raise exceptions.ServerError(
            f"在数据库中找不到正在运行的connector {connector_id}"
        )
    connector, task = started_connectors.pop(connector_id)

    del session_type_info[connector.get_session_type()]
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


async def autostart_connectors():
    connectors = [
        connector.connector_id
        for connector in db.get_session_connector_all()
        if connector.autostart
    ]
    tasks = await asyncio.gather(
        *[start_connector(connector_id) for connector_id in connectors],
        return_exceptions=True,
    )
    exceptions = [task for task in tasks if isinstance(task, Exception)]
    if exceptions:
        raise ExceptionGroup("自动启动Connector失败", exceptions)
    return tasks
