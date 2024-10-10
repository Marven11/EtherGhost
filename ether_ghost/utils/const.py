import os
from pathlib import Path


SETTINGS_VERSION = "0.0.1"
DB_FILENAME = "store.db"

# 当前操作系统的数据保存位置
# TODO: 允许用户自定义
if os.name == "posix":
    DATA_FOLDER = Path("~/.local/share/EtherGhost").expanduser()
elif os.name == "nt":
    DATA_FOLDER = Path("~/AppData/Roaming/EtherGhost").expanduser()
elif os.name == "darwin":
    DATA_FOLDER = Path("~/Library/Application Support/EtherGhost").expanduser()
else:
    DATA_FOLDER = Path(os.path.abspath("."))

DATA_FOLDER.mkdir(parents=True, exist_ok=True)

ANTSWORD_ENCODER_FOLDER = DATA_FOLDER / "AntSwordEncoder"

if not ANTSWORD_ENCODER_FOLDER.exists():
    ANTSWORD_ENCODER_FOLDER.mkdir()

    (ANTSWORD_ENCODER_FOLDER / "example-base64.js").write_text(
        """
module.exports = (pwd, data, ext={}) => {
    let randomID = `_0x${Math.random().toString(16).substr(2)}`;
    data[randomID] = Buffer.from(data['_']).toString('base64');
    data[pwd] = `eval(base64_decode($_POST[${randomID}]));`;
    delete data['_'];
    return data;
}
"""
    )

ANTSWORD_DECODER_FOLDER = DATA_FOLDER / "AntSwordDecoder"
ANTSWORD_DECODER_FOLDER.mkdir(exist_ok=True)


UPDATE_CHECK_FILEPATH = DATA_FOLDER / "update_check_time.json"
UPDATE_CHECK_INTERVAL = 86400 * 3


STORE_URL = "sqlite:///" + (DATA_FOLDER / DB_FILENAME).as_posix()
