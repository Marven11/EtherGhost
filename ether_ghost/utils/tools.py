import typing as t
import json
import re
import hashlib
import base64


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


def parse_permission(perm: str):
    """将rwxrwxrwx格式的文件权限解析为755格式的

    Args:
        perm (str): rwxrwxrwx格式的文件权限
    """
    # 难看代码大赏
    result = ""
    if not re.match("^[rwx-]{9}$", perm):
        raise ValueError("Wrong permission format: " + perm)
    nums = list(map({"r": 4, "w": 2, "x": 1, "-": 0}.__getitem__, perm))
    for i in range(0, 9, 3):
        result += str(sum(nums[i : i + 3]))
    return result


def java_repr(obj):
    if isinstance(obj, (str, int)):
        if isinstance(obj, str) and len(obj) > 1000:
            parts = ",".join(
                json.dumps(obj[i : i + 1000]) for i in range(0, len(obj), 1000)
            )
            return 'String.join("", ' + parts + ")"
        return json.dumps(obj)
    if isinstance(obj, list) and all(isinstance(x, str) for x in obj):
        return "(new String[]{" + ",".join(java_repr(x) for x in obj) + "})"
    raise NotImplementedError(f"{type(obj)=}")


def md5_encode(s):
    """将给定的字符串或字节序列转换成MD5"""
    if isinstance(s, str):
        s = s.encode()
    return hashlib.md5(s).hexdigest()


def base64_encode(s: str | bytes):
    """将给定的字符串或字节序列编码成base64"""
    if isinstance(s, str):
        s = s.encode("utf-8")
    return base64.b64encode(s).decode()
