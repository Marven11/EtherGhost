import tempfile
import subprocess
from ..core import exceptions


def nodejs_eval(code, argv):
    with tempfile.NamedTemporaryFile("w", suffix=".js") as f:
        f.write(code)
        f.flush()
        with subprocess.Popen(["node", f.name] + argv, stdout=subprocess.PIPE) as proc:
            proc.wait()
            if proc.returncode != 0:
                raise exceptions.ServerError(
                    f"蚁剑Encoder执行错误，返回值为{proc.returncode}"
                )
            stdout, _ = proc.communicate()
            return stdout
