from pathlib import Path
from uuid import UUID, uuid4
import tempfile

import typing as t

temp_dir = Path(tempfile.gettempdir())
temp_files: t.Dict[UUID, t.Tuple[str, Path]] = {}


def write_temp_blob(filename: str, blob: bytes):
    filepath = temp_dir / f"{str(uuid4())}.blob"
    filepath.write_bytes(blob)
    file_id = uuid4()
    temp_files[file_id] = (filename, filepath)
    return file_id
