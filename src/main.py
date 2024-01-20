from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import asyncio
import session_manager

app = FastAPI()

app.mount("/public", StaticFiles(directory="public"), name="public")

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

