import typing as t
import json
import re
import hashlib
import base64
import shlex


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
            parts = ",".join([
                json.dumps(obj[i : i + 1000]) for i in range(0, len(obj), 1000)
            ])
            return 'String.join("", ' + parts + ")"
        return json.dumps(obj)
    if isinstance(obj, list) and all(isinstance(x, str) for x in obj):
        return "(new String[]{" + ",".join([java_repr(x) for x in obj]) + "})"
    if isinstance(obj, dict):
        # 转换为Java HashMap<String, String>
        entries = []
        for key, value in obj.items():
            if not isinstance(key, str) or not isinstance(value, str):
                # 如果键或值不是字符串，尝试转换为字符串
                key_str = str(key) if not isinstance(key, str) else key
                value_str = str(value) if not isinstance(value, str) else value
                entries.append(f'put({java_repr(key_str)}, {java_repr(value_str)})')
            else:
                entries.append(f'put({java_repr(key)}, {java_repr(value)})')
        if entries:
            return "new java.util.HashMap<String, String>() {{" + ";".join(entries) + ";}}"
        else:
            return "new java.util.HashMap<String, String>()"
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


def shell_join(cmd):
    """将命令参数列表连接为shell转义的字符串"""
    # pyright fix: explicitly convert to list of strings
    quoted_cmd = [shlex.quote(str(arg)) for arg in cmd]
    return ' '.join(quoted_cmd)
