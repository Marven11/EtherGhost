import asyncio
import traceback
import re
import base64
import uuid
import time
import typing as t


from .core import SessionInterface, exceptions, PHPSessionInterface
from .vessel_php.main import get_vessel_client


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
        try:
            server = await asyncio.start_server(
                self.serve_connection, self.listen_host, self.listen_port
            )
        except OSError as exc:
            if exc.errno == 98:
                raise exceptions.ServerError(
                    f"无法绑定{self.listen_host}:{self.listen_port}，是不是被占用了？"
                )
            raise exceptions.ServerError("无法启动代理") from exc
        except Exception as exc:
            raise exceptions.ServerError("无法启动代理") from exc
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


# TODO: 允许用户在设置里指定这两个值
REQUEST_INTERVAL_SHORT = 0.1
REQUEST_INTERVAL_LONG = 2


async def sender(
    state: dict,
    call: t.Callable[..., t.Awaitable],
    socket_id: int,
    reader: asyncio.StreamReader,
):
    while state["socket_open"]:
        # TODO: 允许用户设置这里的buffer大小
        tosend = await reader.read(1024 * 128)
        if not tosend:
            state["socket_open"] = False
            return
        try:
            await call(
                "tcp_socket_write",
                socket_id,
                base64.b64encode(tosend).decode(),
                timeout=1,
            )
        except exceptions.TargetRuntimeError as e:
            if "VESSEL_FAILED" not in str(e):
                raise e
            state["socket_open"] = False
            return
        print(f"[>] sent {len(tosend)} B")
        state["last_communicate_time"] = time.perf_counter()


async def receiver(
    state: dict,
    call: t.Callable[..., t.Awaitable],
    socket_id: int,
    writer: asyncio.StreamWriter,
):
    while state["socket_open"]:
        try:
            towrite = await call(
                "tcp_socket_read",
                socket_id,
                1024 * 128,
                timeout=1,
            )
        except exceptions.TargetRuntimeError as e:
            if "VESSEL_FAILED" not in str(e):
                raise e
            state["socket_open"] = False
            return
        if towrite is None:
            await asyncio.sleep(1)
            continue
        towrite_bytes = base64.b64decode(towrite)
        if not towrite_bytes:
            await asyncio.sleep(
                REQUEST_INTERVAL_SHORT
                if time.perf_counter() - state["last_communicate_time"] < 3
                else REQUEST_INTERVAL_LONG
            )
            continue
        print(f"[<] recv {len(towrite_bytes)} B")
        writer.write(towrite_bytes)
        state["last_communicate_time"] = time.perf_counter()


class VesselTcpForwardServeConnection:
    def __init__(
        self,
        session: PHPSessionInterface,
        load_vessel_client_code: str,
        listen_host: str,
        listen_port: int,
        host: str,
        port: int,
    ):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.host = host
        self.port = port
        self.call = get_vessel_client(session, load_vessel_client_code)
        self.session_key = f"_{uuid.uuid4()}"

    async def serve_connection_raw(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        socket_id = await self.call(
            "tcp_socket_connect", self.host, self.port, timeout=1
        )
        if socket_id is None:
            raise exceptions.ServerError("Cannot connect")
        print(f"[+] Open new socket {socket_id=}")
        state = {
            "socket_open": True,
            "session_key": self.session_key,
            "last_communicate_time": time.perf_counter(),
        }
        try:
            await asyncio.gather(  # type: ignore
                sender(state, self.call, socket_id, reader),  # type: ignore
                receiver(state, self.call, socket_id, writer),  # type: ignore
            )
        finally:
            state["socket_open"] = False
        try:
            await self.call(
                "tcp_socket_close",
                socket_id,
                1024,
                timeout=1,
            )
        except exceptions.TargetRuntimeError as e:
            if "VESSEL_FAILED" not in str(e):
                raise e
            print(f"[x] Socket close failed {socket_id=} {str(e)}")
        print(f"[-] Socket closed {socket_id=}")

    async def serve_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        try:
            await self.serve_connection_raw(reader, writer)
        except Exception:
            writer.close()
            traceback.print_exc()

    async def start_server(self):

        await asyncio.sleep(0.1)
        server = await asyncio.start_server(
            self.serve_connection, self.listen_host, self.listen_port
        )

        return asyncio.create_task(server.serve_forever())


async def start_vessel_forward_tcp(
    session: PHPSessionInterface,
    load_vessel_client_code: str,
    listen_host: str,
    listen_port: int,
    host: str,
    port: int,
) -> asyncio.Task:
    return await VesselTcpForwardServeConnection(
        session,
        load_vessel_client_code,
        listen_host,
        listen_port,
        host,
        port,
    ).start_server()
