import asyncio

from .core.base import SessionInterface
from .session_types import SessionInfo


class SessionConnector:

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


def register_connector(session_type: str):
    def wrapper(clazz: type[SessionConnector]):
        session_connectors[session_type] = clazz
        return clazz

    return wrapper


async def start_connector(session_type: str, config: dict):
    if session_type in started_connectors:
        return
    connector = session_connectors[session_type](config)
    task = asyncio.create_task(connector.run())
    started_connectors[session_type] = connector
    return task
