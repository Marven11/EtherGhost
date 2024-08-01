"""数据库管理，管理session info等信息"""

import os
import typing as t
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4, UUID
import sqlalchemy as sa
from sqlalchemy_utils import UUIDType  # type: ignore
from ..session_types import (
    SessionInfo,
)

from .const import SETTINGS_VERSION, STORE_URL

engine = sa.create_engine(STORE_URL)
OrmSession = sa.orm.sessionmaker(bind=engine)
orm_session = OrmSession()
Base = sa.orm.declarative_base()


class SessionInfoModel(Base):  # type: ignore
    """sqlalchemy的Model，用于在数据库中保存session info"""

    __tablename__ = "session_info"
    record_id = sa.Column(sa.Integer, primary_key=True)
    session_type = sa.Column(sa.String)  # type: ignore
    session_id = sa.Column(UUIDType(binary=False), default=uuid4)  # type: ignore
    name = sa.Column(sa.String)
    note = sa.Column(sa.String)
    location = sa.Column(sa.String)
    connection = sa.Column(sa.JSON)


class SettingsModel(Base):  # type: ignore
    """sqlalchemy的Model，用于在数据库中保存设置"""

    __tablename__ = "settings"
    record_id = sa.Column(sa.Integer, primary_key=True)
    version = sa.Column(sa.String)
    settings = sa.Column(sa.JSON)


@dataclass
class SessionInfoModelTypeHint:
    """SessionInfoModel的type hint
    解决pylint不能正确识别SQLAlchemy属性类型的问题"""

    record_id: int
    session_type: str
    session_id: UUID
    name: str
    note: str
    location: str
    connection: t.Dict[t.Any, t.Any]


Base.metadata.create_all(engine)


# 转换函数


def model_to_info(model: SessionInfoModelTypeHint) -> SessionInfo:
    """将SessionInfoModel(SQLAlchemy的对象)转换成SessionInfo(Pydantic的对象)"""
    connection = {**model.connection}
    result = SessionInfo(
        session_type=model.session_type,
        name=model.name,
        connection=connection,
        session_id=model.session_id,
        note=model.note,
        location=model.location,
    )
    return result


def info_to_model(info: SessionInfo) -> SessionInfoModel:
    """将SessionInfo(Pydantic的对象)转换成SessionInfoModel(SQLAlchemy的对象)"""
    info_dict = info.model_dump()
    return SessionInfoModel(**info_dict)


# 操作数据库


def list_sessions() -> t.List[SessionInfo]:
    """列出数据库中所有的session"""
    return [model_to_info(model) for model in orm_session.query(SessionInfoModel).all()]


def add_session_info(info: SessionInfo):
    """添加一个session"""
    orm_session.add(info_to_model(info))
    orm_session.commit()


def get_session_info_by_id(
    session_id: t.Union[str, UUID]
) -> t.Union[None, SessionInfo]:
    """根据ID查询session，以sessioninfo的形式输出"""
    if isinstance(session_id, str):
        session_id = UUID(session_id)
    model = (
        orm_session.query(SessionInfoModel)
        .filter(SessionInfoModel.session_id == session_id)
        .first()
    )
    if model is None:
        return None
    return model_to_info(model)


def delete_session_info_by_id(
    session_id: t.Union[str, UUID], ignore_unexist=False
) -> bool:
    """根据ID查询session，并将对应的session info转换成session实例"""
    if isinstance(session_id, str):
        session_id = UUID(session_id)
    model = (
        orm_session.query(SessionInfoModel)
        .filter(SessionInfoModel.session_id == session_id)
        .first()
    )
    if model is None:
        return ignore_unexist  # True if ignore_unexist else False
    orm_session.delete(model)
    orm_session.commit()
    return True


def get_settings() -> dict:
    """查询当前设置"""
    model = orm_session.query(SettingsModel).first()
    if model is None:
        return {}
    assert model.version == SETTINGS_VERSION, (
        "The version of the settings is not supported!"
        + " Did you load a newer settings?"
    )
    return model.settings


def set_settings(settings: dict):
    model = orm_session.query(SettingsModel).first()
    if model:
        orm_session.delete(model)
    orm_session.add(SettingsModel(version=SETTINGS_VERSION, settings=settings))
    orm_session.commit()


def ensure_settings():
    """保证当前设置存在，如果不存在设置则将写入默认设置"""
    default_settings = {"theme": "green", "proxy": ""}
    if get_settings() is None:
        set_settings(default_settings)
