"""Session相关API路由"""

from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
from uuid import UUID, uuid4
from functools import wraps
import tempfile
import re
import logging
import typing as t
from pydantic import BaseModel
from fastapi import APIRouter

from .. import session_manager
from ..utils import db
from ..core import SessionException


temp_dir = Path(tempfile.gettempdir())
temp_files: t.Dict[UUID, t.Tuple[str, Path]] = {}


def write_temp_blob(filename: str, blob: bytes):
    filepath = temp_dir / f"{str(uuid4())}.blob"
    filepath.write_bytes(blob)
    file_id = uuid4()
    temp_files[file_id] = (filename, filepath)
    return file_id


logger = logging.getLogger("main")
router = APIRouter()


def remote_path(filepath: str) -> PurePath:
    """自动猜测传入文件路径的类型为unix/windows, 并实例化成PurePath对象"""
    if re.match(r"^[a-zA-Z]:[/\\]", filepath):
        return PureWindowsPath(filepath)
    return PurePosixPath(filepath)


class FileContentRequest(BaseModel):
    current_dir: str
    filename: str
    text: str
    encoding: str


class PhpCodeRequest(BaseModel):
    code: str


def catch_user_error(fn):
    @wraps(fn)
    async def _wraps(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)
        except SessionException as exc:
            return {
                "code": getattr(type(exc), "code", -500),
                "msg": f"{type(exc).__doc__}: {str(exc)}",
            }

    return _wraps


@router.get("/settings")
async def get_settings():
    """获取当前配置"""
    settings = db.get_settings()
    if not settings:
        return {"code": 0, "data": {}}
    return {"code": 0, "data": settings}


@router.post("/settings")
async def set_settings(settings: t.Dict[str, t.Any]):
    """设置当前配置"""
    db.set_settings(settings)
    session_manager.clear_session_cache()
    return {"code": 0, "data": True}
