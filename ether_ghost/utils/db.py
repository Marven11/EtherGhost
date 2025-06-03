"""数据库管理，管理session info等信息"""

import typing as t
from dataclasses import dataclass
from uuid import uuid4, UUID
import sqlalchemy as sa
from sqlalchemy_utils import UUIDType  # type: ignore
from ..session_types import SessionInfo, SessionConnector

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


class SessionConnectorModel(Base):  # type: ignore
    """sqlalchemy的Model，用于在数据库中保存session connector"""

    __tablename__ = "session_connector"
    record_id = sa.Column(sa.Integer, primary_key=True)
    connector_type = sa.Column(sa.String)  # type: ignore
    connector_id = sa.Column(UUIDType(binary=False), default=uuid4)  # type: ignore
    name = sa.Column(sa.String)
    note = sa.Column(sa.String)
    connection = sa.Column(sa.JSON)
    autostart = sa.Column(sa.Boolean)  # run on program startup


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


@dataclass
class SessionConnectorModelTypeHint:
    """SessionConnectorModel的type hint
    解决pylint不能正确识别SQLAlchemy属性类型的问题"""

    record_id: int
    connector_type: str
    connector_id: UUID
    name: str
    note: str
    connection: t.Dict[t.Any, t.Any]
    autostart: bool


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


def model_to_connector(model: SessionConnectorModelTypeHint) -> SessionConnector:
    """将SessionConnectorModel(SQLAlchemy的对象)转换成SessionConnector(Pydantic的对象)"""
    connection = {**model.connection}
    result = SessionConnector(
        connector_type=model.connector_type,
        name=model.name,
        connection=connection,
        connector_id=model.connector_id,
        note=model.note,
        autostart=model.autostart,
    )
    return result


def connector_to_model(connector: dict) -> SessionConnectorModel:
    """将dict转换成SessionConnectorModel(SQLAlchemy的对象)"""
    return SessionConnectorModel(**connector)


# 操作数据库


# TODO: list session by created time
def list_sessions() -> t.List[SessionInfo]:
    """列出数据库中所有的session"""
    return [model_to_info(model) for model in orm_session.query(SessionInfoModel).all()]


def add_session_info(info: SessionInfo):
    """添加一个session"""
    orm_session.add(info_to_model(info))
    orm_session.commit()


def add_session_infos(infos: t.List[SessionInfo]):
    """批量添加多个session"""
    models = [info_to_model(info) for info in infos]
    orm_session.add_all(models)
    orm_session.commit()


def get_session_info_by_id(
    session_id: t.Union[str, UUID],
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


def get_session_by_session_type(session_type: str) -> t.List[SessionInfo]:
    """根据session_type查询所有session"""
    models = (
        orm_session.query(SessionInfoModel)
        .filter(SessionInfoModel.session_type == session_type)
        .all()
    )
    return [model_to_info(model) for model in models]


def delete_session_by_session_type(session_type: str) -> int:
    """根据session_type删除所有session，返回删除的数量"""
    models = (
        orm_session.query(SessionInfoModel)
        .filter(SessionInfoModel.session_type == session_type)
        .all()
    )
    count = len(models)
    for model in models:
        orm_session.delete(model)
    if count > 0:
        orm_session.commit()
    return count


def list_session_connectors() -> t.List[SessionConnector]:
    """列出数据库中所有的session connector"""
    return [
        model_to_connector(model)
        for model in orm_session.query(SessionConnectorModel).all()
    ]


def add_session_connector(connector: SessionConnector):
    """添加一个session connector"""
    orm_session.add(connector_to_model(connector.model_dump()))
    orm_session.commit()


def add_session_connectors(connectors: t.List[SessionConnector]):
    """批量添加多个session connector"""
    models = [connector_to_model(connector.model_dump()) for connector in connectors]
    orm_session.add_all(models)
    orm_session.commit()


def get_session_connector_by_session_type(
    session_type: str,
) -> t.Union[None, SessionConnector]:
    """根据session_type查询session connector"""
    model = (
        orm_session.query(SessionConnectorModel)
        .filter(SessionConnectorModel.session_type == session_type)
        .first()
    )
    if model is None:
        return None
    return model_to_connector(model)


def delete_session_connector_by_session_type(
    session_type: str, ignore_unexist=False
) -> bool:
    """根据session_type删除session connector"""
    model = (
        orm_session.query(SessionConnectorModel)
        .filter(SessionConnectorModel.session_type == session_type)
        .first()
    )
    if model is None:
        return ignore_unexist
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
    if not get_settings():
        set_settings(default_settings)
