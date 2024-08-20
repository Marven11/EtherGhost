import asyncio
import base64
import json
import traceback
import typing as t
import httpx

url = "http://127.0.0.1/vessel-client.php"


async def call(client: httpx.AsyncClient, fn, *args, timeout):
    resp = await client.post(
        url, data={"fn": fn, "args": json.dumps(args), "timeout": timeout}, timeout=3
    )
    data = resp.json()
    print(f"{fn=} {args=} {data=}")
    if data.get("code", None) != 0:
        raise RuntimeError(data["msg"])
    return data["resp"]


async def sender(socket_id: int, reader: asyncio.StreamReader):
    async with httpx.AsyncClient() as client:
        while True:
            tosend = await reader.read(1024)
            if not tosend:
                await asyncio.sleep(0.5)
                continue
            await call(
                client,
                "tcp_socket_write",
                socket_id,
                base64.b64encode(tosend).decode(),
                timeout=1,
            )


async def receiver(socket_id: int, writer: asyncio.StreamWriter):
    async with httpx.AsyncClient() as client:
        while True:
            towrite = await call(
                client,
                "tcp_socket_read",
                socket_id,
                1024,
                timeout=1,
            )
            towrite_bytes = base64.b64decode(towrite)
            if not towrite_bytes:
                await asyncio.sleep(0.5)
                continue
            writer.write(towrite_bytes)


class TcpServeConnection:
    def __init__(
        self,
        listen_host: str,
        listen_port: int,
        host: str,
        port: int,
    ):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.host = host
        self.port = port

    async def serve_connection_raw(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        socket_id = None
        try:
            async with httpx.AsyncClient() as client:
                socket_id = await call(
                    client,
                    "tcp_socket_connect",
                    self.host,
                    self.port,
                    timeout=1,
                )
        except Exception:
            writer.close()
            return

        print(f"{socket_id=}")
        try:
            # TODO: 正确关闭coro, 避免内存泄漏
            await asyncio.gather(
                sender(socket_id, reader),
                receiver(socket_id, writer),
            )
        except Exception:
            pass
        try:
            async with httpx.AsyncClient() as client:
                socket_id = await call(
                    client,
                    "tcp_socket_close",
                    socket_id,
                    1024,
                    timeout=1,
                )
        except Exception:
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


async def main():
    server = TcpServeConnection("127.0.0.1", 8080, "127.0.0.1", 80)
    task = await server.start_server()
    await task


if __name__ == "__main__":
    asyncio.run(main())
