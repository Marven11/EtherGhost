"""
Session连接器管理模块

负责：
- 定义SessionConnector协议接口
- 管理连接器的注册和启动
- 处理session连接和生命周期
"""

from typing import ClassVar, Protocol, Dict, Any
import asyncio
import uuid
import logging


logger = logging.getLogger("core.session_connector")

from .utils import db
from .core import exceptions
from .core.base import SessionInterface, OptionGroup, session_type_info
from .session_types import SessionInfo

connector_sessions: dict[uuid.UUID, SessionInfo] = {}


def get_session(client_id: uuid.UUID):
    return connector_sessions.get(client_id, None)


def get_connector_of_session(client_id: uuid.UUID):
    session = get_session(client_id)
    if not session:
        return None
    connector = [
        connector
        for connector, _ in started_connectors.values()
        if connector.get_session_type() == session.session_type
    ]
    if not connector:
        return None
    return connector.pop()


def list_sessions():
    return list(connector_sessions.values())


def register_session(client_id: uuid.UUID, session_info: SessionInfo):
    connector_sessions[client_id] = session_info


def delete_session(client_id: uuid.UUID):
    del connector_sessions[client_id]


class SessionConnector(Protocol):
    connector_name: ClassVar[str]  # 内部使用的Connector Name, 全局唯一
    connector_name_readable: ClassVar[str]  # 展示给用户的Connector Name
    session_class: ClassVar[type[SessionInterface]]
    options: ClassVar[list[OptionGroup]]

    def __init__(self, connector_id: uuid.UUID, config: dict):
        """提供connector实例对应的connector_id和对应的config"""
        raise NotImplementedError()

    async def run(self):
        raise NotImplementedError()

    def get_session_type(self) -> str:
        """返回正在运行的connector对应的session_type
        connector生成的session_info都由此session_type标记"""
        raise NotImplementedError()

    # 构造session对象与关闭session时传入的是session连接方式相关的config字典
    # 因为构造session对象应该与session的名字和备注等信息无关

    def build_session(self, config: dict) -> SessionInterface:
        raise NotImplementedError()

    async def close_session(self, config: dict):
        raise NotImplementedError()


class DirectSessionConnector(SessionConnector):
    """直接型connector，用于不需要持续运行服务的session类型（如PHP webshell、CMD webshell）"""
    connector_name: ClassVar[str]
    connector_name_readable: ClassVar[str]
    session_class: ClassVar[type[SessionInterface]]
    options: ClassVar[list[OptionGroup]]

    def __init__(self, connector_id: uuid.UUID, config: dict):
        """提供connector实例对应的connector_id和对应的config"""
        self.config = config
        self.connector_id = connector_id

    async def run(self) -> None:
        """直接型connector无需持续运行"""
        pass

    def get_session_type(self) -> str:
        raise NotImplementedError()

    def build_session(self, config: dict) -> SessionInterface:
        raise NotImplementedError()

    async def close_session(self, config: dict):
        pass


session_connectors: dict[str, type[SessionConnector]] = {}
started_connectors: dict[uuid.UUID, tuple[SessionConnector, asyncio.Task]] = {}

# 存储直接型connector的映射：session_type -> connector_type
_direct_connector_registry: Dict[str, str] = {}


def register_direct_connector(session_type: str, connector_cls: type[SessionConnector]):
    """注册一个直接型connector"""
    session_connectors[connector_cls.connector_name] = connector_cls
    _direct_connector_registry[session_type] = connector_cls.connector_name
    return connector_cls


def register_connector(clazz: type[SessionConnector]):
    session_connectors[clazz.connector_name] = clazz
    # register session_type_info when started
    return clazz


def get_connector_for_session_type(session_type: str) -> type[SessionConnector] | None:
    """根据session_type获取对应的connector类"""
    # 先检查是否是直接型connector
    if session_type in _direct_connector_registry:
        connector_name = _direct_connector_registry[session_type]
        return session_connectors.get(connector_name)

    # 如果不是直接型，检查是否有已启动的connector匹配
    for connector, _ in started_connectors.values():
        if connector.get_session_type() == session_type:
            # 返回这个connector的类
            for connector_cls in session_connectors.values():
                if connector_cls.connector_name == connector.connector_name:
                    return connector_cls

    return None


async def start_connector(connector_id: uuid.UUID):
    if connector_id in started_connectors:
        raise exceptions.UserError(f"Connector {connector_id} 已经启动")

    connector_info = db.get_session_connector_by_connector_id(connector_id)
    if connector_info is None:
        raise RuntimeError(f"找不到connector {connector_id}")

    clazz = session_connectors[connector_info.connector_type]
    logger.debug(f"Connector info: {connector_info.connection=}")
    connector = clazz(connector_id, connector_info.connection)
    task = asyncio.create_task(connector.run())

    started_connectors[connector_id] = (connector, task)

    # 注册session_type_info
    session_type = connector.get_session_type()
    session_type_info[session_type] = {
        "constructor": connector.build_session,
        "options": clazz.session_class.conn_options,
        "readable_name": f"{connector_info.name} {clazz.session_class.readable_name}",
        "session_class": clazz.session_class,
    }

    return task


async def stop_connector(connector_id: uuid.UUID):
    if connector_id not in started_connectors:
        raise exceptions.UserError(f"Connector {connector_id} 未启动")

    connector_info = db.get_session_connector_by_connector_id(connector_id)
    if connector_info is None:
        raise exceptions.ServerError(
            f"在数据库中找不到正在运行的connector {connector_id}"
        )
    connector, task = started_connectors.pop(connector_id)

    del session_type_info[connector.get_session_type()]
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


async def autostart_connectors():
    connectors = [
        connector.connector_id
        for connector in db.get_session_connector_all()
        if connector.autostart
    ]
    tasks = await asyncio.gather(
        *[start_connector(connector_id) for connector_id in connectors],
        return_exceptions=True,
    )
    exceptions = [task for task in tasks if isinstance(task, Exception)]
    if exceptions:
        raise ExceptionGroup("自动启动Connector失败", exceptions)
    return tasks


async def example():
    print(f"{session_connectors=}")
    connector = session_connectors["REVERSE_SHELL"](uuid.uuid4(), {"port": 3001})
    asyncio.create_task(connector.run())
    while True:
        for session_info in list_sessions():
            print(f"{session_info=}")
            session = connector.build_session(session_info.connection)
            result = await session.execute_cmd("ls")
            print(result)
            await connector.close_session(session_info.connection)
            await asyncio.sleep(1)
        await asyncio.sleep(0)


# 直接型connector默认实例字典
_direct_connector_instances: dict[str, SessionConnector] = {}


def register_direct_session_class(session_cls):
    """注册一个直接型session类，为其创建一个直接型connector并注册"""
    # 动态创建直接型connector类
    connector_name_value = session_cls.session_type
    connector_name_readable_value = session_cls.readable_name
    session_class_value = session_cls

    class DirectConnector(DirectSessionConnector):
        connector_name = connector_name_value
        connector_name_readable = connector_name_readable_value
        session_class = session_class_value
        options = session_class_value.conn_options

        def get_session_type(self) -> str:
            return self.session_class.session_type

        def build_session(self, config: dict) -> SessionInterface:
            return self.session_class(config)

        async def close_session(self, config: dict) -> None:
            pass

    # 注册到session_connectors
    session_connectors[connector_name_value] = DirectConnector
    # 创建默认实例并存储
    virtual_connector_id = uuid.uuid5(uuid.NAMESPACE_DNS, connector_name_value)
    default_instance = DirectConnector(virtual_connector_id, {})
    _direct_connector_instances[connector_name_value] = default_instance

    # 同时，将session_type映射到connector_name
    _direct_connector_registry[session_cls.session_type] = connector_name_value
    
    # 确保session_type_info中有session_class字段
    if session_cls.session_type in session_type_info:
        session_type_info[session_cls.session_type]["session_class"] = session_cls
    else:
        # 如果session_type_info中还没有注册，则注册完整信息
        session_type_info[session_cls.session_type] = {
            "constructor": session_cls,
            "options": session_cls.conn_options,
            "readable_name": session_cls.readable_name,
            "session_class": session_cls,
        }


def get_connector_instance_by_session_type(
    session_type: str,
) -> SessionConnector | None:
    """根据session_type获取connector实例，优先返回直接型connector的默认实例，然后查找已启动的监听型connector"""
    # 先检查直接型connector
    if session_type in _direct_connector_instances:
        return _direct_connector_instances[session_type]
    # 然后检查已启动的监听型connector
    for connector, _ in started_connectors.values():
        if connector.get_session_type() == session_type:
            return connector
    # 如果都没有找到，但session_type在session_type_info中，则动态创建直接型connector
    if session_type in session_type_info:
        info = session_type_info[session_type]
        # 优先使用session_class字段，如果不存在则使用constructor字段（可能是类）
        session_cls = info.get("session_class")
        if session_cls is None:
            session_cls = info.get("constructor")
            if session_cls is None:
                # 两个字段都没有，无法创建直接型connector
                return None
        # 确保session_cls是一个类，而不是函数
        # 如果constructor是函数（即build_session方法），那么session_cls应该是session_class字段，我们已经优先使用它
        # 但如果session_cls仍然是函数，则无法创建直接型connector，返回None
        if not isinstance(session_cls, type):
            # 尝试从已启动的connector中查找
            for connector, _ in started_connectors.values():
                if connector.get_session_type() == session_type:
                    return connector
            return None
        
        # 参考register_direct_session_class的逻辑
        connector_name_value = session_cls.session_type
        connector_name_readable_value = session_cls.readable_name
        session_class_value = session_cls

        class DirectConnector(DirectSessionConnector):
            connector_name = connector_name_value
            connector_name_readable = connector_name_readable_value
            session_class = session_class_value
            options = session_class_value.conn_options

            def get_session_type(self) -> str:
                return self.session_class.session_type

            def build_session(self, config: dict) -> SessionInterface:
                return self.session_class(config)

            async def close_session(self, config: dict) -> None:
                pass

        # 注册到session_connectors
        session_connectors[connector_name_value] = DirectConnector
        # 创建默认实例并存储
        virtual_connector_id = uuid.uuid5(uuid.NAMESPACE_DNS, connector_name_value)
        default_instance = DirectConnector(virtual_connector_id, {})
        _direct_connector_instances[session_type] = default_instance
        # 同时，将session_type映射到connector_name
        _direct_connector_registry[session_type] = connector_name_value
        return default_instance
    return None
