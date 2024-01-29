"""webui的后台部分"""
import typing as t
import re
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
from uuid import UUID

import chardet
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from . import session_manager, session_types, sessions
from .sessions import Session

DIR = Path(__file__).parent
app = FastAPI()
app.mount("/public", StaticFiles(directory=DIR / "public"), name="public")


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
    return response


@app.get("/session")
async def get_sessions(session_id: t.Union[UUID, None] = None):
    """列出所有的session或者查找session"""
    if session_id is None:
        return {"code": 0, "data": session_manager.list_sessions_readable()}
    session: t.Union[
        session_types.SessionInfo, None
    ] = session_manager.get_session_info_by_id(session_id)
    if not session:
        return {"code": -400, "msg": "没有这个session"}
    return {"code": 0, "data": session}


@app.post("/test_webshell")
async def test_webshell(session_info: session_types.SessionInfo):
    """测试webshell"""
    session = session_manager.session_info_to_session(session_info)
    try:
        result = await session.test_usablility()
        return {"code": 0, "data": result}
    except sessions.NetworkError as exc:
        return {"code": -500, "data": "网络错误：" + str(exc)}


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
    session: t.Union[Session, None] = session_manager.get_session_by_id(session_id)
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    try:
        result = await session.execute_cmd(cmd)
        return {"code": 0, "data": result}
    except sessions.NetworkError as exc:
        return {"code": -500, "msg": "网络错误: " + str(exc)}
    except sessions.UnexpectedError as exc:
        return {"code": -500, "msg": "未知错误: " + str(exc)}


@app.get("/session/{session_id}/get_pwd")
async def session_get_pwd(session_id: UUID):
    """获取session的pwd"""
    session: t.Union[Session, None] = session_manager.get_session_by_id(session_id)
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    try:
        result = await session.get_pwd()
        return {"code": 0, "data": result}
    except sessions.NetworkError as exc:
        return {"code": -500, "msg": "网络错误: " + str(exc)}
    except sessions.UnexpectedError as exc:
        return {"code": -500, "msg": "未知错误: " + str(exc)}


@app.get("/session/{session_id}/list_dir")
async def session_list_dir(session_id: UUID, current_dir: str):
    """使用session列出某个目录"""
    session: t.Union[Session, None] = session_manager.get_session_by_id(session_id)
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    try:
        result = await session.list_dir(current_dir)
        return {"code": 0, "data": result}
    except sessions.NetworkError as exc:
        return {"code": -500, "msg": "网络错误: " + str(exc)}
    except sessions.UnexpectedError as exc:
        return {"code": -500, "msg": "未知错误: " + str(exc)}


@app.get("/session/{session_id}/get_file_contents")
async def session_get_file_contents(session_id: UUID, current_dir: str, filename: str):
    """使用session获取文件内容"""
    session: t.Union[Session, None] = session_manager.get_session_by_id(session_id)
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    content = None
    try:
        path = remote_path(current_dir) / filename
        content = await session.get_file_contents(str(path))
    except sessions.NetworkError as exc:
        return {"code": -500, "msg": "网络错误: " + str(exc)}
    except sessions.FileError as exc:
        return {"code": -500, "msg": "文件读取错误: " + str(exc)}
    except sessions.UnexpectedError as exc:
        return {"code": -500, "msg": "未知错误: " + str(exc)}
    try:
        detected_encoding = chardet.detect(content)["encoding"]
        if detected_encoding is None:
            detected_encoding = "UTF-8"
        text = content.decode(detected_encoding)
        return {"code": 0, "data": {"text": text, "encoding": detected_encoding}}
    except UnicodeDecodeError as exc:
        return {
            "code": -500,
            "msg": f"编码错误：检测出编码为{detected_encoding}，但是解码失败：" + str(exc),
        }


@app.delete("/session/{session_id}")
async def delete_session(session_id: UUID):
    """删除session"""
    session: t.Union[
        session_types.SessionInfo, None
    ] = session_manager.get_session_info_by_id(session_id)
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    session_manager.delete_session_info_by_id(session_id)
    return {"code": 0, "data": True}


@app.get("/utils/changedir")
async def changedir(folder: str, entry: str):
    """改变当前文件夹，为了保证正确实现使用了pathlib"""
    result = None
    if entry == "..":
        result = remote_path(folder).parent
    elif entry == ".":
        result = folder
    else:
        result = remote_path(folder) / entry
    return {"code": 0, "data": result}


@app.get("/")
async def hello_world():
    """转到主页"""
    return RedirectResponse("/public/index.html")
