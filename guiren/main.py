"""webui的后台部分"""

import logging
import typing as t
import re
import base64
import secrets
from contextlib import asynccontextmanager
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
from uuid import UUID

import chardet
from fastapi import FastAPI, Response, File, Form, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import session_manager, session_types, core, db, upload_file_status
from .core import SessionInterface, PHPSessionInterface, session_type_info

token = secrets.token_bytes(16).hex()
logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.warning("Your token is %s", token)
    yield


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


class FileContentRequest(BaseModel):
    current_dir: str
    filename: str
    text: str
    encoding: str


class PhpCodeRequest(BaseModel):
    code: str


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
async def get_sessiontype_conn_options(sessiontype: str):
    """查找session type对应的选项"""
    if sessiontype not in session_type_info:
        return {"code": -400, "msg": "没有这个session type"}
    conn_options = session_type_info[sessiontype]["options"]
    return {"code": 0, "data": conn_options}


@app.get("/session")
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
async def get_session(session_id: UUID):
    """查找session"""
    session: t.Union[session_types.SessionInfo, None] = (
        session_manager.get_session_info_by_id(session_id)
    )
    if not session:
        return {"code": -400, "msg": "没有这个session"}
    return {"code": 0, "data": session}


@app.post("/test_webshell")
async def test_webshell(session_info: session_types.SessionInfo):
    """测试webshell"""
    session = session_manager.session_info_to_session(session_info)
    try:
        result = await session.test_usablility()
        if not result:
            return {"code": 0, "data": {"success": False, "msg": "Webshell无法使用"}}
        return {"code": 0, "data": {"success": True, "msg": "Webshell可以使用"}}
    except core.UnexpectedError as exc:
        return {
            "code": 0,
            "data": {
                "success": False,
                "msg": "未知错误，Webshell不可以使用：" + str(exc),
            },
        }
    except core.NetworkError as exc:
        return {
            "code": 0,
            "data": {
                "success": False,
                "msg": "网络错误，Webshell不可以使用：" + str(exc),
            },
        }


@app.post("/update_webshell")
async def update_webshell(session_info: session_types.SessionInfo):
    """添加或更新webshell"""
    if session_manager.get_session_info_by_id(session_info.session_id):
        session_manager.delete_session_info_by_id(session_info.session_id)
    session_manager.add_session_info(session_info)
    return {"code": 0, "data": True}


@app.get("/session/{session_id}/execute_cmd")
async def session_execute_cmd(session_id: UUID, cmd: str):
    """使用session执行shell命令"""
    session: t.Union[SessionInterface, None] = session_manager.get_session_by_id(
        session_id
    )
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    try:
        result = await session.execute_cmd(cmd)
        return {"code": 0, "data": result}
    except core.NetworkError as exc:
        return {"code": -500, "msg": "网络错误: " + str(exc)}
    except core.UnexpectedError as exc:
        return {"code": -500, "msg": "未知错误: " + str(exc)}


@app.get("/session/{session_id}/get_pwd")
async def session_get_pwd(session_id: UUID):
    """获取session的pwd"""
    session: t.Union[SessionInterface, None] = session_manager.get_session_by_id(
        session_id
    )
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    try:
        result = await session.get_pwd()
        return {"code": 0, "data": result}
    except core.NetworkError as exc:
        return {"code": -500, "msg": "网络错误: " + str(exc)}
    except core.UnexpectedError as exc:
        return {"code": -500, "msg": "未知错误: " + str(exc)}


@app.get("/session/{session_id}/list_dir")
async def session_list_dir(session_id: UUID, current_dir: str):
    """使用session列出某个目录"""
    session: t.Union[SessionInterface, None] = session_manager.get_session_by_id(
        session_id
    )
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    try:
        result = await session.list_dir(current_dir)
        return {"code": 0, "data": result}
    except core.NetworkError as exc:
        return {"code": -500, "msg": "网络错误: " + str(exc)}
    except core.UnexpectedError as exc:
        return {"code": -500, "msg": "未知错误: " + str(exc)}


@app.get("/session/{session_id}/move_file")
async def session_move_file(session_id: UUID, filepath: str, new_filepath):
    """使用session列出某个目录"""
    session: t.Union[SessionInterface, None] = session_manager.get_session_by_id(
        session_id
    )
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    try:
        await session.move_file(filepath, new_filepath)
        return {"code": 0, "data": True}
    except core.FileError as exc:
        return {"code": -500, "msg": "文件错误: " + str(exc)}
    except core.NetworkError as exc:
        return {"code": -500, "msg": "网络错误: " + str(exc)}
    except core.UnexpectedError as exc:
        return {"code": -500, "msg": "未知错误: " + str(exc)}


@app.get("/session/{session_id}/get_file_contents")
async def session_get_file_contents(session_id: UUID, current_dir: str, filename: str):
    """使用session获取文件内容"""
    session: t.Union[SessionInterface, None] = session_manager.get_session_by_id(
        session_id
    )
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    content, detected_encoding = None, None
    try:
        path = remote_path(current_dir) / filename
        content = await session.get_file_contents(str(path))
    except core.NetworkError as exc:
        return {"code": -500, "msg": "网络错误: " + str(exc)}
    except core.FileError as exc:
        return {"code": -500, "msg": "文件读取错误: " + str(exc)}
    except core.UnexpectedError as exc:
        return {"code": -500, "msg": "未知错误: " + str(exc)}
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
async def session_put_file_contents(session_id: UUID, request: FileContentRequest):
    """使用session写入文件内容"""
    session: t.Union[SessionInterface, None] = session_manager.get_session_by_id(
        session_id
    )
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    try:
        path = remote_path(request.current_dir) / request.filename
        content = request.text.encode(request.encoding)
        success = await session.put_file_contents(str(path), content)
        return {"code": 0, "data": success}
    except core.NetworkError as exc:
        return {"code": -500, "msg": "网络错误: " + str(exc)}
    except core.FileError as exc:
        return {"code": -500, "msg": "文件写入错误: " + str(exc)}
    except core.UnexpectedError as exc:
        return {"code": -500, "msg": "未知错误: " + str(exc)}


@app.post("/session/{session_id}/upload_file")
async def session_upload_file(
    session_id: UUID,
    file: UploadFile = File(),
    folder: str = Form(),
):
    """使用session写入文件内容"""
    session: t.Union[SessionInterface, None] = session_manager.get_session_by_id(
        session_id
    )
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    filename = file.filename
    content = await file.read()
    if filename is None:
        return {"code": -400, "msg": "错误: 没有文件名"}
    try:
        path = remote_path(folder) / filename
        with upload_file_status.record_upload_file(
            session_id, folder, filename
        ) as status_changer:
            success = await session.upload_file(
                str(path), content, callback=status_changer
            )
        return {"code": 0, "data": success}
    except core.NetworkError as exc:
        return {"code": -500, "msg": "网络错误: " + str(exc)}
    except core.FileError as exc:
        return {"code": -500, "msg": "文件写入错误: " + str(exc)}
    except core.UnexpectedError as exc:
        return {"code": -500, "msg": "未知错误: " + str(exc)}


@app.get("/session/{session_id}/delete_file")
async def session_delete_file(session_id: UUID, current_dir: str, filename: str):
    """使用session获取文件内容"""
    session: t.Union[SessionInterface, None] = session_manager.get_session_by_id(
        session_id
    )
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    try:
        path = remote_path(current_dir) / filename
        result = await session.delete_file(str(path))
        return {"code": 0, "data": result}
    except core.NetworkError as exc:
        return {"code": -500, "msg": "网络错误: " + str(exc)}
    except core.FileError as exc:
        return {"code": -500, "msg": "文件删除错误: " + str(exc)}
    except core.UnexpectedError as exc:
        return {"code": -500, "msg": "未知错误: " + str(exc)}


@app.get("/session/{session_id}/file_upload_status")
async def session_get_file_upload_status(session_id: UUID):
    """读取session正在上传的文件"""
    result = upload_file_status.get_session_uploading_file(session_id)
    return {"code": 0, "data": result}


@app.get("/session/{session_id}/basicinfo")
async def session_get_basicinfo(session_id: UUID):
    """读取session的相关信息"""
    session: t.Union[SessionInterface, None] = session_manager.get_session_by_id(
        session_id
    )
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    try:
        result = await session.get_basicinfo()
        return {"code": 0, "data": result}
    except core.NetworkError as exc:
        return {"code": -500, "msg": "网络错误: " + str(exc)}
    except core.UnexpectedError as exc:
        return {"code": -500, "msg": "未知错误: " + str(exc)}


@app.get("/session/{session_id}/download_phpinfo")
async def session_download_phpinfo(session_id: UUID):
    """下载phpinfo"""
    session: t.Union[SessionInterface, None] = session_manager.get_session_by_id(
        session_id
    )
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    if not isinstance(session, PHPSessionInterface):
        return {"code": -400, "msg": "指定的session不是PHP Session"}
    content = None
    try:
        content = await session.download_phpinfo()

        headers = {
            "Content-Disposition": "attachment; filename=phpinfo.html"
        }  # 设置文件名
        return Response(
            content=content, media_type="application/octet-stream", headers=headers
        )
    except core.NetworkError as exc:
        return {"code": -500, "msg": "网络错误: " + str(exc)}
    except core.UnexpectedError as exc:
        return {"code": -500, "msg": "未知错误: " + str(exc)}


@app.post("/session/{session_id}/php_eval")
async def session_php_eval(session_id: UUID, request: PhpCodeRequest):
    """下载phpinfo"""
    session: t.Union[SessionInterface, None] = session_manager.get_session_by_id(
        session_id
    )
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    if not isinstance(session, PHPSessionInterface):
        return {"code": -400, "msg": "指定的session不是PHP Session"}
    result = None
    try:
        code = request.code
        result = await session.php_eval(code)
        return {"code": 0, "data": result}
    except core.NetworkError as exc:
        return {"code": -500, "msg": "网络错误: " + str(exc)}
    except core.UnexpectedError as exc:
        return {"code": -500, "msg": "未知错误: " + str(exc)}


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


@app.get("/utils/join_path")
async def join_path(folder: str, entry: str):
    """改变当前文件夹，为了保证正确实现使用了pathlib"""
    result = None
    if entry == "..":
        result = remote_path(folder).parent
    elif entry == ".":
        result = folder
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
