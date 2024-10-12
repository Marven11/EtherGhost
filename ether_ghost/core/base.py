"""定义session的接口和输入输出"""

import typing as t
from dataclasses import dataclass
from ..utils.user_agents import random_user_agent
from ..utils.db import get_settings

import httpx

USER_AGENT = random_user_agent()
session_type_info = {}


class ConnOptionAlternative(t.TypedDict):
    name: str
    value: str


class ConnOption(t.TypedDict):
    id: str
    name: str
    type: t.Literal["text", "select", "checkbox"]
    placeholder: t.Union[str, None]
    default_value: t.Any
    alternatives: t.Union[t.List[ConnOptionAlternative], None]


class ConnOptionGroup(t.TypedDict):
    name: str
    options: t.List[ConnOption]


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

    async def mkdir(self, dir_path: str) -> None:
        """创建文件夹"""
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

    async def copy_file(self, filepath: str, new_filepath: str) -> None:
        """复制一份当前文件到新的位置"""
        raise NotImplementedError()

    async def upload_file(
        self, filepath: str, content: bytes, callback: t.Union[t.Callable, None] = None
    ) -> bool:
        """上传文件，内容是一个字节序列，不是已经解码的字符串"""
        raise NotImplementedError()

    async def download_file(
        self, filepath: str, callback: t.Union[t.Callable, None] = None
    ) -> bytes:
        """下载，内容是一个字节序列，不是已经解码的字符串"""
        raise NotImplementedError()

    async def send_bytes_over_tcp(
        self,
        host: str,
        port: int,
        content: bytes,
        send_method: t.Union[str, None] = None,
    ) -> t.Union[bytes, None]:
        """把一串字节通过TCP发送到其他机器上，可以指定对应的发送方法"""
        raise NotImplementedError()

    async def get_send_tcp_support_methods(self) -> t.List[str]:
        """得到发送字节支持的TCP方法"""
        raise NotImplementedError()

    async def get_pwd(self) -> str:
        """获取当前的目录"""
        raise NotImplementedError()

    async def get_basicinfo(self) -> t.List[BasicInfoEntry]:
        """获取当前的基本信息"""
        raise NotImplementedError()

    async def open_reverse_shell(self, host: str, port: int) -> None:
        """打开一个反弹shell"""
        raise NotImplementedError()


class PHPSessionInterface(SessionInterface):
    """PHP Session接口"""

    async def download_phpinfo(self) -> bytes:
        """获取当前的phpinfo文件"""
        raise NotImplementedError()

    async def php_eval(self, code: str) -> str:
        """执行给定的代码，使用eval"""
        raise NotImplementedError()

    async def php_eval_beforebody(self, code: str) -> t.Tuple[int, str]:
        """执行给定的代码，不使用任何wrapper

        保证在此之前不使用echo等输出body正文，但不能自动从HTML中提取代码输出"""
        # 为了保证能正常地打开和关闭php session
        raise NotImplementedError()

    async def emulated_antsword(self, body: bytes) -> t.Tuple[int, str]:
        """解析蚁剑给的body, 返回raw的HTTP返回码和内容"""
        raise NotImplementedError()


def register_session(cls):
    """装饰session class, 注册一个session
    class必需的属性
      - .conn_options (t.List[ConnOptionGroup]):
        注明所需的每个选项
      - .readable_name (str):
        session的名字
      - .session_type (str):
        session的ID，可以包含大小写字符和下划线
    """
    session_type_info[cls.session_type] = {
        "constructor": cls,
        "options": cls.conn_options,
        "readable_name": cls.readable_name,
    }
    return cls


def get_http_client(**kwargs):
    proxy = None
    if get_settings().get("proxy", None):
        proxy = get_settings().get("proxy", None)
    return httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, proxy=proxy, **kwargs)
