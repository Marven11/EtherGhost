from typing import ClassVar
import asyncio

from .core.base import SessionInterface, OptionGroup, session_type_info
from .session_types import SessionInfo


class SessionConnector:
    connector_name: ClassVar[str]
    session_class: ClassVar[type[SessionInterface]]
    options: ClassVar[list[OptionGroup]]

    def __init__(self, config: dict):
        raise NotImplementedError()

    async def run(self):
        raise NotImplementedError()

    async def list_sessions(self) -> list[SessionInfo]:
        raise NotImplementedError()

    # 构造session对象与关闭session时传入的是session连接方式相关的config字典
    # 因为构造session对象应该与session的名字和备注等信息无关

    def build_session(self, config: dict) -> SessionInterface:
        raise NotImplementedError()

    async def close_session(self, config: dict):
        raise NotImplementedError()


session_connectors: dict[str, type[SessionConnector]] = {}
started_connectors: dict[str, tuple[SessionConnector, asyncio.Task]] = {}


def build_session(session_type: str, config: dict):
    if session_type not in session_connectors:
        raise RuntimeError(f"找不到session: {session_type!r}")
    if session_type not in started_connectors:
        raise RuntimeError(f"{session_type!r}对应的connector未启动")
    connector, _ = started_connectors[session_type]
    return connector.build_session(config)


def register_connector(clazz: type[SessionConnector]):
    session_type = clazz.session_class.session_type
    session_connectors[session_type] = clazz
    session_type_info[session_type] = {
        "constructor": lambda config: build_session(session_type, config),
        "options": clazz.session_class.conn_options,
        "readable_name": clazz.session_class.readable_name,
    }
    return clazz


async def start_connector(session_type: str, config: dict):
    if session_type in started_connectors:
        return
    connector = session_connectors[session_type](config)
    task = asyncio.create_task(connector.run())
    started_connectors[session_type] = (connector, task)
    return task


async def example():
    print(f"{session_connectors=}")
    connector = session_connectors["REVERSE_SHELL"]({"port": 3001})
    asyncio.create_task(connector.run())
    while True:
        for session_info in await connector.list_sessions():
            print(f"{session_info=}")
            session = connector.build_session(session_info.connection)
            result = await session.execute_cmd("ls")
            print(result)
            await connector.close_session(session_info.connection)
            await asyncio.sleep(1)
        await asyncio.sleep(0)
