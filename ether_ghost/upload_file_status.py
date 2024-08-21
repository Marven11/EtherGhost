from contextlib import contextmanager
import typing as t
import uuid

upload_file_status = {}



@contextmanager
def record_upload_file(session_id: t.Union[uuid.UUID, str], folder: str, filename: str):

    if session_id not in upload_file_status:
        upload_file_status[session_id] = {}
    upload_file_status[session_id][(folder, filename)] = 0

    def change_status(done_coro: int, max_coro: int, done_bytes: int, max_bytes: int):
        percentage = done_coro / max_coro
        upload_file_status[session_id][(folder, filename)] = (
            percentage,
            done_bytes,
            max_bytes,
        )

    try:
        yield change_status
    finally:
        del upload_file_status[session_id][(folder, filename)]
        if not upload_file_status[session_id]:
            del upload_file_status[session_id]


def get_session_uploading_file(session_id):
    return [
        {
            "folder": folder,
            "file": file,
            "percentage": percentage,
            "done_bytes": done_bytes,
            "max_bytes": max_bytes,
        }
        for (folder, file), (
            percentage,
            done_bytes,
            max_bytes,
        ) in upload_file_status.get(session_id, {}).items()
    ]
