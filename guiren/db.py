"""数据库管理，管理session info等信息"""

import os
from uuid import uuid4, UUID
import typing as t
from pathlib import Path
import sqlalchemy as sa
from sqlalchemy_utils import ChoiceType, UUIDType
from .session_types import (
    SessionType,
    SessionInfo,
    SessionConnOnelinePHP,
    type_to_class,
)

DB_FILENAME = "guiren.db"


def get_file_uri() -> Path:
    """根据当前操作系统返回数据保存位置"""
    if os.name == "posix":
        data_path = Path("~/.local/share").expanduser() / DB_FILENAME
    elif os.name == "nt":
        data_path = Path("~/AppData/Roaming").expanduser() / DB_FILENAME
    elif os.name == "darwin":
        data_path = Path("~/Library/Containers").expanduser() / DB_FILENAME
    else:
        data_path = Path(os.path.abspath(".")) / DB_FILENAME

    return "sqlite:///" + data_path.absolute().as_posix()


engine = sa.create_engine(get_file_uri())
OrmSession = sa.orm.sessionmaker(bind=engine)
orm_session = OrmSession()
Base = sa.orm.declarative_base()


class SessionInfoModel(Base):
    """sqlalchemy的Model，用于在数据库中保存session info"""

    __tablename__ = "session_info"
    record_id = sa.Column(sa.Integer, primary_key=True)
    session_type = sa.Column(ChoiceType(SessionType, impl=sa.String()))
    session_id = sa.Column(UUIDType(binary=False), default=uuid4)
    name = sa.Column(sa.String)
    note = sa.Column(sa.String)
    location = sa.Column(sa.String)
    connection = sa.Column(sa.JSON)


Base.metadata.create_all(engine)


# 转换函数


def model_to_info(model: SessionInfoModel) -> SessionInfo:
    if model.session_type not in type_to_class:
        raise TypeError(f"session type not found: {model.session_type}")
    connection = type_to_class[model.session_type](**model.connection)
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
    info = info.model_dump()
    return SessionInfoModel(**info)


# 操作数据库


def list_sessions() -> t.List[SessionInfo]:
    return [model_to_info(model) for model in orm_session.query(SessionInfoModel).all()]


def add_session_info(info: SessionInfo):
    orm_session.add(info_to_model(info))
    orm_session.commit()


def get_session_info_by_id(
    session_id: t.Union[str, UUID]
) -> t.Union[None, SessionInfo]:
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
    if isinstance(session_id, str):
        session_id = UUID(session_id)
    model = get_session_info_by_id(session_id)
    if model is None:
        return ignore_unexist  # True if ignore_unexist else False
    orm_session.delete(model)
    orm_session.commit()
    return True


# 测试函数


def test_init():
    sessions_info = [
        SessionInfo(
            connection=SessionConnOnelinePHP(
                method="POST",
                url="http://127.0.0.1:8081/shell.php",
                password="data",
            ),
            name="本地webshell",
            session_type=SessionType.ONELINE_PHP,
            session_id=uuid4(),
            note="",
            location="US",
        ),
        SessionInfo(
            connection=SessionConnOnelinePHP(
                method="POST",
                url="http://127.0.0.1:8081/shell.php",
                password="data",
            ),
            name="另一个webshell",
            session_type=SessionType.ONELINE_PHP,
            session_id=uuid4(),
            note="",
            location="US",
        ),
        SessionInfo(
            connection=SessionConnOnelinePHP(
                method="POST",
                url="http://127.0.0.1:8081/shell.php",
                password="data",
            ),
            name="又一个webshell",
            session_type=SessionType.ONELINE_PHP,
            session_id=uuid4(),
            note="",
            location="US",
        ),
        SessionInfo(
            connection=SessionConnOnelinePHP(
                method="POST",
                url="http://127.0.0.1:8081/shell.php",
                password="data",
            ),
            name="还是一个webshell",
            session_type=SessionType.ONELINE_PHP,
            session_id=uuid4(),
            note="",
            location="US",
        ),
    ]
    for sessinfo in sessions_info:
        add_session_info(sessinfo)


def test():
    info_uuid = uuid4()
    info = SessionInfo(
        connection=SessionConnOnelinePHP(
            method="POST",
            url="http://127.0.0.1:8081/shell.php",
            password="data",
        ),
        name="本地webshell",
        session_type=SessionType.ONELINE_PHP,
        session_id=info_uuid,
        note="",
        location="US",
    )
    print(list_sessions())
    add_session_info(info)
    model = get_session_info_by_id(info_uuid)
    print(model)


if __name__ == "__main__":
    test()
