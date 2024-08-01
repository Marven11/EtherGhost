"""webui的后台部分"""

import asyncio
import logging
import typing as t
import tempfile
import re
import functools
import base64
import secrets
from contextlib import asynccontextmanager
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
from uuid import UUID, uuid4

import chardet
from fastapi import FastAPI, Response, File, Form, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .utils import db

from . import session_manager, session_types, core, upload_file_status
from .tcp_proxies import start_psudo_tcp_proxy
from .core import SessionInterface, PHPSessionInterface, session_type_info

token = secrets.token_bytes(16).hex()
logger = logging.getLogger("main")

# uuid: (filename, blob_path)


class FileContentRequest(BaseModel):
    current_dir: str
    filename: str
    text: str
    encoding: str


class PhpCodeRequest(BaseModel):
    code: str


class ProxyRequest(BaseModel):
    type: t.Literal["psudo_forward_proxy"]
    session_id: UUID
    listen_host: t.Union[str, None]
    listen_port: int
    host: str
    port: int
    send_method: t.Union[str, None]


temp_dir = Path(tempfile.gettempdir())
temp_files: t.Dict[UUID, t.Tuple[str, Path]] = {}

psudo_tcp_proxies: t.Dict[int, t.Tuple[ProxyRequest, asyncio.Task]] = {}


@asynccontextmanager
async def lifespan(api: FastAPI):
    # logger.warning("Your token is %s", token)
    db.ensure_settings()
    yield
    for _, filepath in temp_files.values():
        if filepath.exists():
            filepath.unlink()
    temp_files.clear()
    for tpl in psudo_tcp_proxies.values():
        server = tpl[-1]
        try:
            server.cancel()
        except asyncio.exceptions.CancelledError:
            pass
    psudo_tcp_proxies.clear()


DIR = Path(__file__).parent
app = FastAPI(lifespan=lifespan)
app.mount("/public", StaticFiles(directory=DIR / "public"), name="public")
app.mount("/assets", StaticFiles(directory=DIR / "public" / "assets"), name="assets")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源，这里设置为所有
    allow_credentials=True,  # 是否允许携带凭据
    allow_methods=["*"],  # 允许的 HTTP 方法
    allow_headers=["*"],  # 允许的头部信息
)


def write_temp_blob(filename: str, blob: bytes):
    filepath = temp_dir / f"{str(uuid4())}.blob"
    filepath.write_bytes(blob)
    file_id = uuid4()
    temp_files[file_id] = (filename, filepath)
    return file_id


def remote_path(filepath: str) -> PurePath:
    """自动猜测传入文件路径的类型为unix/windows, 并实例化成PurePath对象"""
    if re.match(r"^[a-zA-Z]:[/\\]", filepath):
        return PureWindowsPath(filepath)
    return PurePosixPath(filepath)


@app.middleware("http")
async def set_no_cache(request, call_next) -> Response:
    """让浏览器不要缓存文件"""
    response: Response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Access-Control-Allow-Origin"] = (
        "*"  # TODO: remove me, this is added for testing.
    )
    return response


def catch_user_error(fn):
    @functools.wraps(fn)
    async def _wraps(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)
        except core.SessionException as exc:
            return {
                "code": type(exc).code,
                "msg": f"{type(exc).__doc__}: {str(exc)}",
            }

    return _wraps


@app.get("/sessiontype")
async def get_sessiontype():
    """查找所有支持的session type"""
    return {
        "code": 0,
        "data": [
            {"id": type_id, "name": type_info["readable_name"]}
            for type_id, type_info in session_type_info.items()
        ],
    }


@app.get("/sessiontype/{sessiontype}/conn_options")
@catch_user_error
async def get_sessiontype_conn_options(sessiontype: str):
    """查找session type对应的选项"""
    if sessiontype not in session_type_info:
        return {"code": -400, "msg": "没有这个session type"}
    conn_options = session_type_info[sessiontype]["options"]
    return {"code": 0, "data": conn_options}


@app.get("/session")
@catch_user_error
async def get_sessions(session_id: t.Union[UUID, None] = None):
    """列出所有的session或者查找session"""
    if session_id is None:
        return {"code": 0, "data": session_manager.list_sessions_readable()}
    session: t.Union[session_types.SessionInfo, None] = (
        session_manager.get_session_info_by_id(session_id)
    )
    if not session:
        return {"code": -400, "msg": "没有这个session"}
    return {"code": 0, "data": session}


@app.get("/session/{session_id}")
@catch_user_error
async def get_session(session_id: UUID):
    """查找session"""
    session: t.Union[session_types.SessionInfo, None] = (
        session_manager.get_session_info_by_id(session_id)
    )
    if not session:
        return {"code": -400, "msg": "没有这个session"}
    return {"code": 0, "data": session}


@app.post("/test_webshell")
@catch_user_error
async def test_webshell(session_info: session_types.SessionInfo):
    """测试webshell"""
    session = session_manager.session_info_to_session(session_info)
    result = await session.test_usablility()
    if not result:
        return {"code": 0, "data": {"success": False, "msg": "Webshell无法使用"}}
    return {"code": 0, "data": {"success": True, "msg": "Webshell可以使用"}}


@app.post("/update_webshell")
async def update_webshell(session_info: session_types.SessionInfo):
    """添加或更新webshell"""
    if session_manager.get_session_info_by_id(session_info.session_id):
        session_manager.delete_session_info_by_id(session_info.session_id)
    session_manager.add_session_info(session_info)
    return {"code": 0, "data": session_info.session_id}


@app.get("/session/{session_id}/execute_cmd")
@catch_user_error
async def session_execute_cmd(session_id: UUID, cmd: str):
    """使用session执行shell命令"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    result = await session.execute_cmd(cmd)
    return {"code": 0, "data": result}


@app.get("/session/{session_id}/get_pwd")
@catch_user_error
async def session_get_pwd(session_id: UUID):
    """获取session的pwd"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    result = await session.get_pwd()
    return {"code": 0, "data": result}


@app.get("/session/{session_id}/list_dir")
@catch_user_error
async def session_list_dir(session_id: UUID, current_dir: str):
    """使用session列出某个目录"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    result = await session.list_dir(current_dir)
    return {"code": 0, "data": result}


@app.get("/session/{session_id}/move_file")
@catch_user_error
async def session_move_file(session_id: UUID, filepath: str, new_filepath):
    """使用session移动某个文件"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    await session.move_file(filepath, new_filepath)
    return {"code": 0, "data": True}


@app.get("/session/{session_id}/get_file_contents")
@catch_user_error
async def session_get_file_contents(session_id: UUID, current_dir: str, filename: str):
    """使用session获取文件内容"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    content, detected_encoding = None, None
    path = remote_path(current_dir) / filename
    content = await session.get_file_contents(str(path))
    try:
        detected_encoding = chardet.detect(content)["encoding"]
        # TODO: Linux的编码一般是utf-8, windows的编码一般是utf-8
        if detected_encoding is None or detected_encoding == "ascii":
            detected_encoding = "utf-8"
        text = content.decode(detected_encoding)
        return {"code": 0, "data": {"text": text, "encoding": detected_encoding}}
    except UnicodeDecodeError as exc:
        return {
            "code": -500,
            "msg": f"编码错误：检测出编码为{detected_encoding}，但是解码失败："
            + str(exc),
        }


@app.post("/session/{session_id}/put_file_contents")
@catch_user_error
async def session_put_file_contents(session_id: UUID, request: FileContentRequest):
    """使用session写入文件内容"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    path = remote_path(request.current_dir) / request.filename
    content = request.text.encode(request.encoding)
    success = await session.put_file_contents(str(path), content)
    return {"code": 0, "data": success}


@app.post("/session/{session_id}/upload_file")
@catch_user_error
async def session_upload_file(
    session_id: UUID,
    file: UploadFile = File(),
    folder: str = Form(),
):
    """使用session写入文件内容"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    filename = file.filename
    content = await file.read()
    if filename is None:
        return {"code": -400, "msg": "错误: 没有文件名"}
    path = remote_path(folder) / filename
    with upload_file_status.record_upload_file(
        session_id, folder, filename
    ) as status_changer:
        success = await session.upload_file(str(path), content, callback=status_changer)
    return {"code": 0, "data": success}


@app.get("/session/{session_id}/download_file")
@catch_user_error
async def session_download_file(
    session_id: UUID,
    folder: str,
    filename: str,
):
    """使用session写入文件内容"""
    # 一个文件最多只有几十兆，浏览器应该可以轻松处理
    # 如果用户想要用webshell下载几百兆的文件。。。那应该是用户自己的问题
    filepath = remote_path(folder) / filename
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    content = await session.download_file(str(filepath))
    file_id = write_temp_blob(filename, content)
    return {
        "code": 0,
        "data": {
            "file_id": file_id,
        },
    }


@app.get("/session/{session_id}/delete_file")
@catch_user_error
async def session_delete_file(session_id: UUID, current_dir: str, filename: str):
    """使用session获取文件内容"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    path = remote_path(current_dir) / filename
    result = await session.delete_file(str(path))
    return {"code": 0, "data": result}


@app.get("/session/{session_id}/supported_send_tcp_methods")
@catch_user_error
async def session_supported_send_tcp_methods(
    session_id: UUID,
):
    """使用session发送一段字节到某个TCP端口"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    result = await session.get_send_tcp_support_methods()
    return {
        "code": 0,
        "data": result,
    }


@app.post("/session/{session_id}/send_bytes_tcp")
@catch_user_error
async def session_send_bytes_tcp(
    session_id: UUID,
    host: str = Form(),
    port: int = Form(),
    content_b64: str = Form(),
    send_method: t.Union[str, None] = Form(),
):
    """使用session发送一段字节到某个TCP端口"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    result = await session.send_bytes_over_tcp(
        host, port, base64.b64decode(content_b64), send_method
    )
    if result is None:
        return {"code": -600, "msg": "受控端发送TCP失败"}
    return {
        "code": 0,
        "data": base64.b64encode(result),
    }


@app.get("/session/{session_id}/file_upload_status")
@catch_user_error
async def session_get_file_upload_status(session_id: UUID):
    """读取session正在上传的文件"""
    result = upload_file_status.get_session_uploading_file(session_id)
    return {"code": 0, "data": result}


@app.get("/session/{session_id}/basicinfo")
@catch_user_error
async def session_get_basicinfo(session_id: UUID):
    """读取session的相关信息"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    result = await session.get_basicinfo()
    return {"code": 0, "data": result}


@app.get("/session/{session_id}/download_phpinfo")
@catch_user_error
async def session_download_phpinfo(session_id: UUID):
    """下载phpinfo"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    if not isinstance(session, PHPSessionInterface):
        return {"code": -400, "msg": "指定的session不是PHP Session"}
    content = await session.download_phpinfo()

    headers = {"Content-Disposition": "attachment; filename=phpinfo.html"}  # 设置文件名
    return Response(
        content=content, media_type="application/octet-stream", headers=headers
    )


@app.post("/session/{session_id}/php_eval")
@catch_user_error
async def session_php_eval(session_id: UUID, request: PhpCodeRequest):
    """eval对应代码"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    if not isinstance(session, PHPSessionInterface):
        return {"code": -400, "msg": "指定的session不是PHP Session"}
    code = request.code
    result = await session.php_eval(code)
    return {"code": 0, "data": result}


@app.post("/session/{session_id}/php_eval_raw")
@catch_user_error
async def session_php_eval_raw(session_id: UUID, request: PhpCodeRequest):
    """eval对应代码，不使用wrapper，直接返回对应的响应码和body"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    if not isinstance(session, PHPSessionInterface):
        return {"code": -400, "msg": "指定的session不是PHP Session"}
    status_code, content = await session.php_eval_raw(request.code)
    return Response(status_code=status_code, content=content)


@app.delete("/session/{session_id}")
async def delete_session(session_id: UUID):
    """删除session"""
    session: t.Union[session_types.SessionInfo, None] = (
        session_manager.get_session_info_by_id(session_id)
    )
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    session_manager.delete_session_info_by_id(session_id)
    return {"code": 0, "data": True}


@app.get("/forward_proxy/list")
@catch_user_error
async def forward_proxy_list():
    def get_session_name(sess_id):
        sess_info = session_manager.get_session_info_by_id(sess_id)
        if not sess_info:
            return "未知Session"
        return sess_info.name

    return {
        "code": 0,
        "data": [
            {
                "type": "psudo_forward_proxy",
                "session_id": proxy_request.session_id,
                "session_name": get_session_name(proxy_request.session_id),
                "listen_host": proxy_request.listen_host,
                "listen_port": proxy_request.listen_port,
                "host": proxy_request.host,
                "port": proxy_request.port,
                "send_method": proxy_request.send_method,
            }
            for proxy_request, _ in psudo_tcp_proxies.values()
        ],
    }


@app.post("/forward_proxy/create_psudo_proxy")
@catch_user_error
async def forward_proxy_create_psudo_proxy(request: ProxyRequest):
    if request.listen_port in psudo_tcp_proxies:
        return {"code": -400, "msg": "端口已占用"}
    if request.listen_host is None:
        request.listen_host = "0.0.0.0"
    session: SessionInterface = session_manager.get_session_by_id(request.session_id)
    # TODO: check request.type
    server_task = await start_psudo_tcp_proxy(
        session,
        request.listen_host,
        request.listen_port,
        request.host,
        request.port,
        request.send_method,
    )
    psudo_tcp_proxies[request.listen_port] = (
        request,
        server_task,
    )
    return {"code": 0, "data": True}


@app.delete("/forward_proxy/{listen_port}/")
@catch_user_error
async def forward_proxy_delete(listen_port: int):
    server_task = psudo_tcp_proxies[listen_port][-1]
    try:
        server_task.cancel()
    except asyncio.exceptions.CancelledError:
        pass
    del psudo_tcp_proxies[listen_port]
    return {"code": 0, "data": True}


@app.get("/utils/fetch_downloaded_file/{file_id}")
async def fetch_downloaded_file(file_id: UUID):
    if file_id not in temp_files:
        raise HTTPException(status_code=404, detail="File not found")
    (filename, filepath) = temp_files[file_id]
    return FileResponse(path=filepath, filename=filename)


@app.get("/utils/join_path")
async def join_path(folder: str, entry: str):
    """改变当前文件夹，为了保证正确实现使用了pathlib"""
    result = None
    if entry == "..":
        result = remote_path(folder).parent
    elif entry == ".":
        result = remote_path(folder)
    else:
        result = remote_path(folder) / entry
    return {"code": 0, "data": result}


@app.get("/settings")
async def get_settings():
    """获取当前配置"""
    settings = db.get_settings()
    if not settings:
        return {"code": 0, "data": {}}
    return {"code": 0, "data": settings}


@app.post("/settings")
async def set_settings(settings: t.Dict[str, t.Any]):
    """设置当前配置"""
    db.set_settings(settings)
    return {"code": 0, "data": True}


@app.get("/")
async def hello_world():
    """转到主页"""
    return RedirectResponse("/public/index.html")
