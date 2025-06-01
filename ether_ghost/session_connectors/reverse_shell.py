import asyncio
import uuid
from ..sessions.reverse_shell import ReverseShellSession, REVERSE_SHELL_SESSION_TYPE
from ..session_types import SessionInfo
from ..session_connector import SessionConnector, register_connector


@register_connector(REVERSE_SHELL_SESSION_TYPE)
class ReverseShellConnector(SessionConnector):

    def __init__(self, config: dict):
        self.port = config["port"]
        self.socket = None
        self.session_infos: dict[str, SessionInfo] = {}
        self.connections: dict[
            str, tuple[asyncio.StreamReader, asyncio.StreamWriter]
        ] = {}
        self.session_count = 0

    def build_session(self, config: dict) -> ReverseShellSession:
        if (
            "connection_id" not in config
            or not isinstance(config["connection_id"], str)
            or config["connection_id"] not in self.connections
        ):
            raise RuntimeError("socket not found")
        reader, writer = self.connections[config["connection_id"]]
        return ReverseShellSession(config, reader, writer)

    async def run(self):

        async def handle_client(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ):
            client_id = uuid.uuid4()
            self.session_count += 1
            self.connections[str(client_id)] = (reader, writer)
            self.session_infos[str(client_id)] = SessionInfo(
                session_type=REVERSE_SHELL_SESSION_TYPE,
                name=f"反弹Shell #{self.session_count}",
                connection={"connection_id": str(client_id)},
                session_id=client_id,
                note=f"Reverse shell {client_id}",
            )

        self.socket = await asyncio.start_server(handle_client, "0.0.0.0", self.port)
        async with self.socket:
            await self.socket.serve_forever()

    async def list_sessions(self) -> list[SessionInfo]:
        return list(self.session_infos.values())
