from typing import ClassVar, Protocol
import asyncio
import uuid


from .utils import db
from .core import exceptions
from .core.base import SessionInterface, OptionGroup, session_type_info
from .session_types import SessionInfo

connector_sessions: dict[uuid.UUID, SessionInfo] = {}


def get_session(client_id: uuid.UUID):
    return connector_sessions.get(client_id, None)


def list_sessions():
    return list(connector_sessions.values())


def register_session(client_id: uuid.UUID, session_info: SessionInfo):
    connector_sessions[client_id] = session_info


def delete_session(client_id: uuid.UUID):
    del connector_sessions[client_id]


class SessionConnector(Protocol):
    connector_name: ClassVar[str]  # 内部使用的Connector Name, 全局唯一
    session_class: ClassVar[type[SessionInterface]]
    options: ClassVar[list[OptionGroup]]

    def __init__(self, connector_id: uuid.UUID, config: dict):
        """提供connector实例对应的connector_id和对应的config"""
        raise NotImplementedError()

    async def run(self):
        raise NotImplementedError()

    def get_session_type(self) -> str:
        """返回正在运行的connector对应的session_type
        connector生成的session_info都由此session_type标记"""
        raise NotImplementedError()

    # 构造session对象与关闭session时传入的是session连接方式相关的config字典
    # 因为构造session对象应该与session的名字和备注等信息无关

    def build_session(self, config: dict) -> SessionInterface:
        raise NotImplementedError()

    async def close_session(self, config: dict):
        raise NotImplementedError()


session_connectors: dict[str, type[SessionConnector]] = {}
started_connectors: dict[uuid.UUID, tuple[SessionConnector, asyncio.Task]] = {}


def register_connector(clazz: type[SessionConnector]):
    session_connectors[clazz.connector_name] = clazz
    # register session_type_info when started
    return clazz


async def start_connector(connector_id: uuid.UUID):
    if connector_id in started_connectors:
        raise exceptions.UserError(f"Connector {connector_id} 已经启动")

    connector_info = db.get_session_connector_by_connector_id(connector_id)
    if connector_info is None:
        raise RuntimeError(f"找不到connector {connector_id}")

    clazz = session_connectors[connector_info.connector_type]
    print(f"{connector_info.connection=}")
    connector = clazz(connector_id, connector_info.connection)
    task = asyncio.create_task(connector.run())

    started_connectors[connector_id] = (connector, task)
    session_type_info[connector.get_session_type()] = {
        "constructor": connector.build_session,
        "options": clazz.session_class.conn_options,
        "readable_name": f"{connector_info.name} {clazz.session_class.readable_name}",
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
    clazz = session_connectors[connector_info.connector_type]
    connector, task = started_connectors.pop(connector_id)

    del session_type_info[connector.get_session_type()]
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


async def example():
    print(f"{session_connectors=}")
    connector = session_connectors["REVERSE_SHELL"](uuid.uuid4(), {"port": 3001})
    asyncio.create_task(connector.run())
    while True:
        for session_info in list_sessions():
            print(f"{session_info=}")
            session = connector.build_session(session_info.connection)
            result = await session.execute_cmd("ls")
            print(result)
            await connector.close_session(session_info.connection)
            await asyncio.sleep(1)
        await asyncio.sleep(0)
