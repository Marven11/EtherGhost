"""webui的后台部分"""
import typing as t
from uuid import UUID
from pathlib import Path
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from . import session_manager, session_types, sessions
from .sessions import Session

DIR = Path(__file__).parent
app = FastAPI()
app.mount("/public", StaticFiles(directory=DIR / "public"), name="public")


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


@app.delete("/session/{session_id}")
async def delete_session(session_id: UUID):
    """使用session执行shell命令"""
    session: t.Union[
        session_types.SessionInfo, None
    ] = session_manager.get_session_info_by_id(session_id)
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    session_manager.delete_session_info_by_id(session_id)
    return {"code": 0, "data": True}


@app.get("/")
async def hello_world():
    """转到主页"""
    return RedirectResponse("/public/index.html")
