"""session在执行代码时产生的exceptions"""


class SessionException(Exception):
    """使用sessions时产生的错误"""


class UnknownError(SessionException):
    """未知错误"""


class NetworkError(SessionException):
    """网络错误"""


class FileError(SessionException):
    """文件错误"""


class UserError(SessionException):
    """用户操作失误"""
