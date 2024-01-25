import typing as t
from dataclasses import dataclass

@dataclass
class DirectoryEntry:
    name: str
    permission: str
    entry_type: t.Literal["directory", "file", "unknown"] = "file"


class Session:
    async def execute_cmd(self, cmd: str) -> str:
        raise NotImplementedError()

    async def test_usablility(self) -> bool:
        raise NotImplementedError()

    async def list_dir(self, dir_path: str) -> t.List[DirectoryEntry]:
        raise NotImplementedError()

    async def get_file_contents(self, filepath: str) -> bytes:
        raise NotImplementedError()

    async def get_pwd(self) -> str:
        raise NotImplementedError()
