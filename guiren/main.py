from uuid import UUID
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from . import session_manager
from .session.session import Session

app = FastAPI()

app.mount("/public", StaticFiles(directory="public"), name="public")


@app.post("/find_session")
async def find_session(session_id: UUID):
    """根据ID寻找对应的session"""
    session: Session = session_manager.get_session_by_id(session_id)
    return {"code": 0, "data": session is not None}


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
    return RedirectResponse("/public/index.html")


