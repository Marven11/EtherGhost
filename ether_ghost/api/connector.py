import functools
from uuid import UUID
from fastapi import APIRouter

from ..utils import db
from ..core import exceptions

from .. import (
    session_types,
    session_connector,
    core,
)


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


@router.get("/connectortype")
async def api_get_connectortype():
    """查找所有支持的session type"""
    return {
        "code": 0,
        "data": list(session_connector.session_connectors.keys()),
    }


@router.get("/connectortype/{connector_name}/conn_options")
@catch_user_error
async def api_get_connectortype_conn_options(connector_name: str):
    """查找sessionr type对应的选项"""
    if connector_name not in session_connector.session_connectors:
        raise core.UserError(f"没有这个Connector {connector_name}")
    connector_class = session_connector.session_connectors[connector_name]
    return {
        "code": 0,
        "data": connector_class.options,
    }


@router.get("/connector/all")
async def list_connectors():
    return {"code": 0, "data": db.list_session_connectors()}


@router.get("/connector/started")
async def list_started_connectors():
    return {"code": 0, "data": list(session_connector.started_connectors.keys())}


@router.get("/connector/{connector_id}")
@catch_user_error
async def get_connector(connector_id: UUID):
    result = db.get_session_connector_by_connector_id(connector_id)
    if not result:
        raise exceptions.UserError(f"未找到Connector: {connector_id}")
    return {
        "code": 0,
        "data": db.get_session_connector_by_connector_id(connector_id)
    }

@router.post("/connector")
async def add_or_update_connector(connector_info: session_types.SessionConnectorInfo):
    """添加或更新connector"""
    if db.get_session_connector_by_connector_id(connector_info.connector_id):
        db.update_session_connector(connector_info)
        return {
            "code": 0,
            "data": {"action": "update", "connector_id": connector_info.connector_id},
        }
    else:
        db.add_session_connector(connector_info)
        return {
            "code": 0,
            "data": {"action": "add", "connector_id": connector_info.connector_id},
        }


@router.get("/connector/{connector_id}/start")
@catch_user_error
async def start_connector(connector_id: UUID):
    """根据connector id找到connector并启动"""

    await session_connector.start_connector(connector_id)
    return {"code": 0, "data": True}


@router.get("/connector/{connector_id}/stop")
@catch_user_error
async def stop_connector(connector_id: UUID):
    """根据connector id找到connector并停止"""
    await session_connector.stop_connector(connector_id)
    return {"code": 0, "data": True}
