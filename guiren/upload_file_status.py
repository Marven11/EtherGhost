from contextlib import contextmanager

upload_file_status = {}


@contextmanager
def record_upload_file(session_id, folder, filename):
    if session_id not in upload_file_status:
        upload_file_status[session_id] = {}
    upload_file_status[session_id][(folder, filename)] = 0

    def change_status(percentage: float):
        upload_file_status[session_id][(folder, filename)] = percentage

    yield change_status

    del upload_file_status[session_id][(folder, filename)]
    if not upload_file_status[session_id]:
        del upload_file_status[session_id]


def get_session_uploading_file(session_id):
    return [
        {"folder": folder, "file": file, "percentage": percentage}
        for (folder, file), percentage in upload_file_status.get(session_id, {}).items()
    ]
