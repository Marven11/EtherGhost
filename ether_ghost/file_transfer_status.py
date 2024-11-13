from contextlib import contextmanager
import typing as t
import uuid

file_transfer_status: t.Dict[
    uuid.UUID,
    t.Dict[
        t.Tuple[str, str],  # folder, filename
        t.Tuple[float, int, int],  # percentage done_bytes, max_bytes
    ],
] = {}

download_file_status: t.Dict[
    uuid.UUID,
    t.Dict[
        t.Tuple[str, str],  # folder, filename
        t.Tuple[float, int, int],  # percentage done_bytes, max_bytes
    ],
] = {}


@contextmanager
def record_upload_file(session_id: uuid.UUID, folder: str, filename: str):

    if session_id not in file_transfer_status:
        file_transfer_status[session_id] = {}
    file_transfer_status[session_id][(folder, filename)] = (0, 0, 0)

    def change_status(done_coro: int, max_coro: int, done_bytes: int, max_bytes: int):
        percentage = done_coro / max_coro
        file_transfer_status[session_id][(folder, filename)] = (
            percentage,
            done_bytes,
            max_bytes,
        )

    try:
        yield change_status
    finally:
        if (folder, filename) in file_transfer_status[session_id]:
            del file_transfer_status[session_id][(folder, filename)]
        if not file_transfer_status[session_id]:
            del file_transfer_status[session_id]


@contextmanager
def record_download_file(session_id: uuid.UUID, folder: str, filename: str):

    if session_id not in download_file_status:
        download_file_status[session_id] = {}
    download_file_status[session_id][(folder, filename)] = (0, 0, 0)

    def change_status(done_coro: int, max_coro: int, done_bytes: int, max_bytes: int):
        percentage = done_coro / max_coro
        download_file_status[session_id][(folder, filename)] = (
            percentage,
            done_bytes,
            max_bytes,
        )

    try:
        yield change_status
    finally:
        if (folder, filename) in download_file_status[session_id]:
            del download_file_status[session_id][(folder, filename)]
        if not download_file_status[session_id]:
            del download_file_status[session_id]


def get_session_uploading_file(session_id: uuid.UUID):
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
        ) in file_transfer_status.get(session_id, {}).items()
    ]


def get_session_downloading_file(session_id: uuid.UUID):
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
        ) in download_file_status.get(session_id, {}).items()
    ]
