from uuid import UUID
import asyncio
import functools
import typing as t

from fastapi import APIRouter
from pydantic import BaseModel


from .. import session_manager, core


from ..tcp_proxies import (
    start_psudo_tcp_proxy,
    start_vessel_forward_tcp,
)
from ..core import SessionInterface, PHPSessionInterface
from ..vessel_php.main import start_vessel_server


class ProxyRequest(BaseModel):
    type: t.Literal["psudo_forward_proxy", "vessel_forward_tcp"]
    session_id: UUID
    listen_host: t.Union[str, None]
    listen_port: int
    host: str
    port: int
    send_method: t.Union[str, None]


router = APIRouter()
tcp_forward_proxies: t.Dict[int, t.Tuple[ProxyRequest, asyncio.Task]] = {}


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


@router.get("/forward_proxy/list")
@catch_user_error
async def forward_proxy_list():
    def get_session_name(sess_id):
        sess_info = session_manager.get_session_info_by_id(sess_id)
        if not sess_info:
            return "未知Session"
        return sess_info.name

    return {
        "code": 0,
        "data": [
            {
                "type": proxy_request.type,
                "session_id": proxy_request.session_id,
                "session_name": get_session_name(proxy_request.session_id),
                "listen_host": proxy_request.listen_host,
                "listen_port": proxy_request.listen_port,
                "host": proxy_request.host,
                "port": proxy_request.port,
                "send_method": proxy_request.send_method,
            }
            for proxy_request, _ in tcp_forward_proxies.values()
        ],
    }


@router.post("/forward_proxy/create_psudo_proxy")
@catch_user_error
async def forward_proxy_create_psudo_proxy(request: ProxyRequest):
    if request.listen_port in tcp_forward_proxies:
        return {"code": -400, "msg": "端口已占用"}
    if request.listen_host is None:
        request.listen_host = "0.0.0.0"
    session: SessionInterface = session_manager.get_session_by_id(request.session_id)
    if request.type == "psudo_forward_proxy":
        server_task = await start_psudo_tcp_proxy(
            session,
            request.listen_host,
            request.listen_port,
            request.host,
            request.port,
            request.send_method,
        )
        tcp_forward_proxies[request.listen_port] = (
            request,
            server_task,
        )
        return {"code": 0, "data": True}
    elif request.type == "vessel_forward_tcp":
        if not isinstance(session, PHPSessionInterface):
            return {"code": -400, "msg": "Vessel当前只支持PHP webshell"}

        client_code = await start_vessel_server(session)

        server_task = await start_vessel_forward_tcp(
            session=session,
            load_vessel_client_code=client_code,
            listen_host=request.listen_host,
            listen_port=request.listen_port,
            host=request.host,
            port=request.port,
        )
        tcp_forward_proxies[request.listen_port] = (
            request,
            server_task,
        )
        return {"code": 0, "data": True}
    return {"code": -400, "msg": f"不支持的代理类型：{request.type}"}


@router.delete("/forward_proxy/{listen_port}/")
@catch_user_error
async def forward_proxy_delete(listen_port: int):
    server_task = tcp_forward_proxies[listen_port][-1]
    try:
        server_task.cancel()
    except asyncio.exceptions.CancelledError:
        pass
    del tcp_forward_proxies[listen_port]
    return {"code": 0, "data": True}
