"""session在执行代码时产生的exceptions"""

class SessionException(Exception):
    """使用sessions时产生的错误"""


class NetworkError(Exception):
    """网络错误"""


class UnexpectedError(SessionException):
    """意料之外的错误"""


class FileError(SessionException):
    """文件操作错误"""
