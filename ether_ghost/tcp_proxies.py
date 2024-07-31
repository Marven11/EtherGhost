import asyncio
import traceback
import re
import typing as t


from .core import SessionInterface


class PsudoTcpServeConnection:
    def __init__(
        self,
        session: SessionInterface,
        listen_host: str,
        listen_port: int,
        host: str,
        port: int,
        send_method: t.Union[str, None],
    ):
        self.session = session
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.host = host
        self.port = port
        self.send_method = send_method

    async def serve_connection_raw(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        request = b""
        while not request.endswith(b"\r\n\r\n"):
            request += await reader.read(1024)
        if b"HTTP/1.1" not in request:
            writer.write(
                b"HTTP/1.1 400 Bad Request\r\nContent-Length: 14\r\nConnection: close\r\n\r\n400 bad req sb\r\n\r\n"
            )
            writer.write_eof()
            writer.close()
            return
        if b"Connection: close" not in request:
            request = request.replace(
                b"HTTP/1.1\r\n", b"HTTP/1.1\r\nConnection: close\r\n", 1
            )
        response = await self.session.send_bytes_over_tcp(
            self.host, self.port, request, self.send_method
        )
        if response is None:
            writer.write_eof()
            writer.close()
            return
        if b"Server: " in response:
            response = re.sub(rb"Server: .+\r\n", b"Server: sbserver\r\n", response)
        writer.write(response)
        writer.write_eof()
        writer.close()
        return

    async def serve_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        try:
            await self.serve_connection_raw(reader, writer)
        except Exception:
            traceback.print_exc()

    async def start_server(self) -> asyncio.Task:
        server = await asyncio.start_server(
            self.serve_connection, self.listen_host, self.listen_port
        )
        task = asyncio.create_task(server.serve_forever())
        return task


async def start_psudo_tcp_proxy(
    session: SessionInterface,
    listen_host: str,
    listen_port: int,
    host: str,
    port: int,
    send_method: t.Union[str, None],
) -> asyncio.Task:
    return await PsudoTcpServeConnection(
        session, listen_host, listen_port, host, port, send_method
    ).start_server()
