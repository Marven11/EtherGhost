class SessionException(Exception):
    pass


class NetworkError(Exception):
    pass


class UnexpectedError(SessionException):
    """意料之外的错误"""


class FileError(SessionException):
    """文件操作错误"""
