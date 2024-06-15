"""定义session的接口和输入输出"""

import typing as t
from dataclasses import dataclass


@dataclass
class DirectoryEntry:
    """文件夹中某一项的信息"""

    name: str
    permission: str
    filesize: int
    entry_type: t.Literal["dir", "file", "link-dir", "link-file", "unknown"] = "file"


@dataclass
class BasicInfoEntry:
    """有关session的一项基本信息"""

    key: str
    value: str


# Session对象会在处理一个请求的时候创建，请求结束时立即丢弃
# 所以Session对象基本上是无状态的，状态会在请求结束后被丢弃

class SessionInterface:
    """Session接口"""

    async def execute_cmd(self, cmd: str) -> str:
        """在目标上执行命令"""
        raise NotImplementedError()

    async def test_usablility(self) -> bool:
        """测试session的可用性"""
        raise NotImplementedError()

    async def list_dir(self, dir_path: str) -> t.List[DirectoryEntry]:
        """列出某个文件夹中的内容，包括`.`和`..`，如果没有内容则会填充`..`"""
        raise NotImplementedError()

    async def get_file_contents(
        self, filepath: str, max_size: int = 1024 * 200
    ) -> bytes:
        """获取文件的内容，内容是一个字节序列，不是已经解码的字符串"""
        raise NotImplementedError()

    async def put_file_contents(self, filepath: str, content: bytes) -> bool:
        """保存文件的内容，内容是一个字节序列，不是已经解码的字符串"""
        raise NotImplementedError()

    async def delete_file(self, filepath: str) -> bool:
        """删除文件"""
        raise NotImplementedError()

    async def move_file(self, filepath: str, new_filepath: str) -> None:
        """移动文件到新的目录"""
        raise NotImplementedError()

    async def get_pwd(self) -> str:
        """获取当前的目录"""
        raise NotImplementedError()

    async def get_basicinfo(self) -> t.List[BasicInfoEntry]:
        """获取当前的基本信息"""
        raise NotImplementedError()


class PHPSessionInterface(SessionInterface):
    """PHP Session接口"""

    async def download_phpinfo(self) -> bytes:
        """获取当前的phpinfo文件"""
        raise NotImplementedError()

    async def php_eval(self, code: str) -> str:
        """执行给定的代码，使用eval"""
        raise NotImplementedError()
