from uuid import UUID
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from . import session_manager, session_types
from .session.session import Session

DIR = Path(__file__).parent
app = FastAPI()
app.mount("/public", StaticFiles(directory=DIR / "public"), name="public")


@app.post("/find_session")
async def find_session(session_id: UUID):
    """根据ID寻找对应的session"""
    session: Session = session_manager.get_session_by_id(session_id)
    return {"code": 0, "data": session is not None}


@app.post("/add_webshell/ONELINE_PHP")
async def add_webshell_oneline_php(
    name: str,
    url: str,
    password: str,
    note: str = "",
    location: str = "",
    session_encoder: str = "",
    http_obfs: str = ""
):
    """添加PHP一句话webshell"""
    session_info = session_types.SessionInfo(
        session_type=session_types.SessionType.ONELINE_PHP,
        name=name,
        connection=session_types.SessionConnOnelinePHP(
            url=url, password=password, method="POST"
        ),
        note=note,
        location=location,
    )
    session_manager.add_session_info(session_info)
    return {"code": 0, "data": True}


@app.post("/session_execute_cmd")
async def session_execute_cmd(session_id: UUID, cmd: str):
    """使用session执行shell命令"""
    session: Session = session_manager.get_session_by_id(session_id)
    if session is None:
        return {"code": -400, "msg": "No such session"}
    result = session.execute_cmd(cmd)
    if result is None:
        return {"code": -400, "msg": "Execute Failed"}
    return {"code": 0, "data": result}


@app.post("/list_session")
async def list_session():
    """列出所有的session"""
    return {"code": 0, "data": session_manager.list_sessions_readable()}


@app.get("/")
async def hello_world():
    """转到主页"""
    return RedirectResponse("/public/index.html")
