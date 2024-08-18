import sys
import importlib
import typing as t

from ..utils import const

# modules文件夹里有多个装有.py文件的文件夹，这些文件会被作为python包导入

modules_folder = const.DATA_FOLDER / "modules"
modules_folder.mkdir(exist_ok=True)
sys.path.append(modules_folder.absolute().as_posix())

encoders_folder = modules_folder / "php_encoders"
encoders_folder.mkdir(exist_ok=True)

decoders_folder = modules_folder / "php_decoders"
decoders_folder.mkdir(exist_ok=True)


def list_custom_encoders():
    return [file.name for file in encoders_folder.glob("*.py")]


def list_custom_decoders():
    return [file.name for file in decoders_folder.glob("*.py")]


def get_encoder(filename: str) -> t.Callable[[str], str]:
    assert filename in list_custom_encoders()
    module = importlib.import_module(f"php_encoders.{filename.removesuffix('.py')}")
    return getattr(module, "encode")


def get_decoder(filename: str) -> t.Tuple[str, t.Callable[[str], str]]:
    assert filename in list_custom_decoders()
    module = importlib.import_module(f"php_decoders.{filename.removesuffix('.py')}")
    return getattr(module, "phpcode"), getattr(module, "decode")
