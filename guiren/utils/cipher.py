import typing as t
from base64 import b64decode
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from .const import DATA_FOLDER


public_key = DATA_FOLDER / "public_key_rsa.pem"
private_key = DATA_FOLDER / "private_key_rsa.pem"


def generate_rsa_keys():

    key = RSA.generate(2048)
    with open(private_key, "wb") as f:
        f.write(key.export_key())

    with open(public_key, "wb") as f:
        f.write(key.publickey().export_key())


def get_rsa_key() -> t.Tuple[bytes, bytes]:
    if not public_key.exists() or not private_key.exists():
        generate_rsa_keys()
    assert public_key.exists() and private_key.exists()
    return public_key.read_bytes(), private_key.read_bytes()


def private_decrypt_rsa(data: t.Union[bytes, str]) -> bytes:
    """解密base64编码的，rsa加密的数据

    Args:
        data (bytes): base64编码的加密数据

    Returns:
        bytes: 解密的数据
    """
    key = RSA.import_key(private_key.read_bytes())

    data = b64decode(data)
    cipher_rsa = PKCS1_OAEP.new(key)
    session_key = cipher_rsa.decrypt(data)
    return session_key
