import asyncio
import traceback

from .core.base import SessionInterface
from .session_types import SessionInfo


class SessionConnector:

    async def run(self):
        raise NotImplementedError()

    async def list_sessions(self) -> list[SessionInfo]:
        raise NotImplementedError()

    def get_session_type(self) -> str:
        raise NotImplementedError()

    def build_session(self, config: dict) -> SessionInterface:
        raise NotImplementedError()


session_connectors: list[type[SessionConnector]] = []


def register_connector(clazz: type[SessionConnector]):
    session_connectors.append(clazz)
    return clazz


async def start_all_connectors():
    async def run_connector(connector: SessionConnector):
        try:
            await connector.run()
        except Exception:
            traceback.print_exc()

    connectors = [connector() for connector in session_connectors]
    tasks = [asyncio.create_task(run_connector(connector)) for connector in connectors]
    return connectors, tasks
