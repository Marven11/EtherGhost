import typing as t
import logging
import base64

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

logger = logging.getLogger("core.sessions.php_raw")


def base64_encode(s):
    """将给定的字符串或字节序列编码成base64"""
    if isinstance(s, str):
        s = s.encode("utf-8")
    return base64.b64encode(s).decode()


@register_session
class PHPWebshellRaw(PHPWebshellCommunication, PHPWebshellActions):
    session_type = "PHP_RAW"
    readable_name = "PHP Raw"
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
        self.https_verify = session_conn.get("https_verify", False)
        self.client = get_http_client(verify=self.https_verify)
        self.timeout_refresh_client = session_conn.get("timeout_refresh_client", True)

    async def php_eval_beforebody(self, code: str) -> t.Tuple[int, str]:
        return await self.submit_http(code)

    async def submit_http(self, payload: t.Union[str, bytes]):
        try:
            response = await self.client.request(
                method="POST", url=self.url, content=payload
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
            raise exceptions.NetworkError("发送HTTP请求到受控端失败：" + str(exc)) from exc
