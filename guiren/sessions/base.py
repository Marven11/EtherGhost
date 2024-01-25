import typing as t


class Session:
    async def execute_cmd(self, cmd: str) -> t.Union[str, None]:
        raise NotImplementedError()

    async def test_usablility(self) -> bool:
        raise NotImplementedError()

class SessionException(Exception):
    pass