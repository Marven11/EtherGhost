from typing import ClassVar
import asyncio

from .core.base import SessionInterface, OptionGroup
from .session_types import SessionInfo


class SessionConnector:
    connector_name: ClassVar[str]
    session_type: ClassVar[str]
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


def register_connector(clazz: type[SessionConnector]):
    session_connectors[clazz.session_type] = clazz
    return clazz


async def start_connector(session_type: str, config: dict):
    if session_type in started_connectors:
        return
    connector = session_connectors[session_type](config)
    task = asyncio.create_task(connector.run())
    started_connectors[session_type] = (connector, task)
    return task
