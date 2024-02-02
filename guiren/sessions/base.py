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

class Session:
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

    async def get_file_contents(self, filepath: str, max_size: int = 1024 * 200) -> bytes:
        """获取文件的内容，内容是一个字节序列，不是已经解码的字符串"""
        raise NotImplementedError()

    async def get_pwd(self) -> str:
        """获取当前的目录"""
        raise NotImplementedError()
