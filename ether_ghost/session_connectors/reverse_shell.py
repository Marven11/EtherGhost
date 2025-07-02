import asyncio
import uuid
from ..core.base import Option, OptionGroup
from ..sessions.reverse_shell import ReverseShellSession
from ..session_types import SessionInfo
from ..session_connector import (
    SessionConnector,
    register_connector,
    register_session,
    delete_session,
    list_sessions,
)


@register_connector
class ReverseShellConnector(SessionConnector):
    connector_name = f"{__name__.replace('.', '_')}_ReverseShellConnector"
    connector_name_readable = f"Linux TCP反弹Shell"
    session_class = ReverseShellSession
    options: list[OptionGroup] = [
        {
            "name": "监听配置",
            "options": [
                Option(
                    id="port",
                    name="监听端口",
                    type="text",
                    placeholder="反弹shell的监听端口",
                    default_value="3001",
                    alternatives=None,
                ),
            ],
        },
        *ReverseShellSession.conn_options
    ]

    def __init__(self, connector_id: uuid.UUID, config: dict):
        self.config = config
        self.connector_id = connector_id
        self.port = int(config["port"])
        self.socket = None
        self.session_infos: dict[str, SessionInfo] = {}
        self.connections: dict[
            str, tuple[asyncio.StreamReader, asyncio.StreamWriter]
        ] = {}
        self.session_count = 0

    def get_session_type(self) -> str:
        return f"{self.connector_name}_{self.connector_id}"

    def build_session(self, config: dict) -> ReverseShellSession:
        if (
            "connection_id" not in config
            or not isinstance(config["connection_id"], str)
            or config["connection_id"] not in self.connections
        ):
            raise RuntimeError("socket not found")
        reader, writer = self.connections[config["connection_id"]]
        return ReverseShellSession(
            {**self.config, **config}, lambda: self.drop_session(config), reader, writer
        )

    async def run(self):

        async def handle_client(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ):
            client_id = uuid.uuid4()
            self.session_count += 1
            self.connections[str(client_id)] = (reader, writer)
            new_session_info = SessionInfo(
                session_type=self.get_session_type(),
                name=f"反弹Shell #{self.session_count}",
                connection={"connection_id": str(client_id)},
                session_id=client_id,
                note=f"Reverse shell {client_id}",
            )
            register_session(client_id, new_session_info)

        self.socket = await asyncio.start_server(handle_client, "0.0.0.0", self.port, limit=1024 * 128)
        async with self.socket:
            await self.socket.serve_forever()

    def drop_session(self, config: dict):
        """在socket失效后直接丢掉socket和对应的session_info"""
        if (
            "connection_id" not in config
            or not isinstance(config["connection_id"], str)
            or config["connection_id"] not in self.connections
        ):
            raise RuntimeError("socket not found")
        del self.connections[config["connection_id"]]
        delete_session(uuid.UUID(config["connection_id"]))

    async def close_session(self, config: dict):
        if (
            "connection_id" not in config
            or not isinstance(config["connection_id"], str)
            or config["connection_id"] not in self.connections
        ):
            raise RuntimeError("socket not found")
        _, writer = self.connections[config["connection_id"]]
        writer.close()
        await writer.wait_closed()
        del self.connections[config["connection_id"]]
        delete_session(uuid.UUID(config["connection_id"]))


async def example():
    connector = ReverseShellConnector(uuid.uuid4(), {"port": 3001})
    task = asyncio.create_task(connector.run())
    try:
        while True:
            for session_info in list_sessions():
                # TODO: 让ReverseShellSession还原ANSI
                session = connector.build_session(session_info.connection)
                result = await session.execute_cmd("ls")
                print(f"{result}")
                print(f"{result=}")
                await connector.close_session(session_info.connection)
            await asyncio.sleep(1)
    finally:
        task.cancel()
