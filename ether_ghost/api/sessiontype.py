import typing as t
import functools

from fastapi import APIRouter

from .. import core


router = APIRouter()


def catch_user_error(fn):
    @functools.wraps(fn)
    async def _wraps(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)
        except core.SessionException as exc:
            return {
                "code": getattr(type(exc), "code", -500),
                "msg": f"{type(exc).__doc__}: {str(exc)}",
            }

    return _wraps


async def get_session_type():
    """查找所有支持的session type"""
    SessionType = t.TypedDict("SessionType", {"id": str, "name": str})
    return [
        SessionType({"id": type_id, "name": type_info["readable_name"]})
        for type_id, type_info in core.session_type_info.items()
    ]


async def get_sessiontype_conn_options(sessiontype: str) -> list[core.OptionGroup]:

    if sessiontype not in core.session_type_info:
        raise core.UserError("没有这个session type")
    return core.session_type_info[sessiontype]["options"]


@router.get("/sessiontype")
async def api_get_sessiontype():
    """查找所有支持的session type"""
    return {
        "code": 0,
        "data": await get_session_type(),
    }


@router.get("/sessiontype/{session_type}/conn_options")
@catch_user_error
async def api_get_sessiontype_conn_options(session_type: str):
    """查找session type对应的选项"""
    return {
        "code": 0,
        "data": await get_sessiontype_conn_options(session_type),
    }
