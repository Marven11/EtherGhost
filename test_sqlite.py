import sqlite3
import os
from pathlib import Path

db_filename = "sqlite.db"
conn = None

def get_file_paths() -> Path:
    """根据当前操作系统返回数据保存位置"""
    # 获取当前操作系统类型
    operating_system = os.name

    if operating_system == "posix":
        # Linux/Unix等操作系统
        data_path = Path("~/.local/share") / db_filename
    elif operating_system == "nt":
        # Windows操作系统
        data_path = Path("~/AppData/Roaming") / db_filename
    elif operating_system == "darwin":
        # macOS操作系统
        data_path = Path("~/Library/Containers") / db_filename
    else:
        # 其他操作系统，默认保存在当前目录下
        data_path = Path(os.path.abspath(".")) / db_filename

    return data_path

def init_db():
    global conn
    conn = sqlite3.connect(get_file_paths())
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greetings (
            message TEXT
        )
    """
    )

    cursor.execute("INSERT INTO greetings (message) VALUES ('Hello world')")

    conn.commit()
    conn.close()

