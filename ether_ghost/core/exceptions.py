"""session在执行代码时产生的exceptions"""


class SessionException(Exception):
    """使用sessions时产生的错误"""


class UserError(SessionException):
    """用户操作失误"""

    code = -400


class ServerError(SessionException):
    code = -500


class UnknownError(ServerError):
    """未知错误"""


class TargetError(SessionException):
    """受控端错误"""

    code = -600


class NetworkError(TargetError):
    """网络错误"""

    code = -600


class FileError(TargetError):
    """文件错误"""

    code = -600


class TargetUnreachable(TargetError):
    """受控端不可达"""

    code = -600


class PayloadOutputError(TargetError):
    """受控端输出错误"""

    code = -600


class TargetRuntimeError(TargetError):
    """受控端运行错误"""

    code = -600
