import base64
import json
import requests
import sys
import time

url = "http://127.0.0.1/vessel-client.php"


def call(fn, *args, timeout):
    resp = requests.post(
        url, data={"fn": fn, "args": json.dumps(args), "timeout": timeout}, timeout=3
    )
    data = resp.json()
    if data.get("code", None) != 0:
        raise RuntimeError(data["msg"])
    return data["resp"]


shell_id = call("spawn_child_shell", "/bin/sh", timeout=1)
print(f"{shell_id=}")
while True:
    time.sleep(0.1)
    cmd = sys.stdin.readline()
    call(
        "child_shell_write_stdin",
        shell_id,
        base64.b64encode(cmd.encode()).decode(),
        timeout=1,
    )
    output = call("child_shell_read_stdout", shell_id, 1024, timeout=1)
    output = base64.b64decode(output)
    sys.stdout.write(output.decode())
    sys.stdout.flush()

call("child_shell_exit", shell_id, timeout=1)
