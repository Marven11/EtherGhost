from typing import ClassVar
import asyncio

from .core.base import SessionInterface, OptionGroup
from .session_types import SessionInfo


class SessionConnector:
    session_type: ClassVar[str]
    options: ClassVar[list[OptionGroup]]

    def __init__(self, config: dict):
        raise NotImplementedError()

    async def run(self):
        raise NotImplementedError()

    async def list_sessions(self) -> list[SessionInfo]:
        raise NotImplementedError()

    def build_session(self, config: dict) -> SessionInterface:
        raise NotImplementedError()


session_connectors: dict[str, type[SessionConnector]] = {}
started_connectors: dict[str, SessionConnector] = {}


def register_connector(clazz: type[SessionConnector]):
    session_connectors[clazz.session_type] = clazz
    return clazz


def list_connectors():
    return list(session_connectors.keys())


async def start_connector(session_type: str, config: dict):
    if session_type in started_connectors:
        return
    connector = session_connectors[session_type](config)
    task = asyncio.create_task(connector.run())
    started_connectors[session_type] = connector
    return task
