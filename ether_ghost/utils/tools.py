import typing as t
import json

from ..core import exceptions


def user_json_loads(data: str, types: t.Union[type, t.Iterable[type]]):
    if not isinstance(types, type):
        types = tuple(types)
    try:
        parsed = json.loads(data)
        if not isinstance(parsed, types):
            raise exceptions.UserError(
                f"无效的JSON数据：需要的数据类型为{types}，输入的是{type(parsed)}，数据为{parsed!r}"
            )
        return parsed
    except json.JSONDecodeError as exc:
        raise exceptions.UserError(f"解码JSON失败: {data!r}") from exc
