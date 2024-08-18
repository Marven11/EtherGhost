import os
from pathlib import Path


SETTINGS_VERSION = "0.0.1"
DB_FILENAME = "store.db"

# 当前操作系统的数据保存位置
if os.name == "posix":
    DATA_FOLDER = Path("~/.local/share/EtherGhost").expanduser()
elif os.name == "nt":
    DATA_FOLDER = Path("~/AppData/Roaming/EtherGhost").expanduser()
elif os.name == "darwin":
    DATA_FOLDER = Path("~/Library/Application Support/EtherGhost").expanduser()
else:
    DATA_FOLDER = Path(os.path.abspath("."))

DATA_FOLDER.mkdir(parents=True, exist_ok=True)

STORE_URL = "sqlite:///" + (DATA_FOLDER / DB_FILENAME).as_posix()