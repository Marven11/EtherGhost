import typing as t
from base64 import b64decode
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
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


def padding_aes256_cbc(s):
    return s + bytes((16 - len(s) % 16) for _ in range(16 - len(s) % 16))


def unpadding_aes256_cbc(s):
    return s[0 : -(s[-1])]


def encrypt_aes256_cbc(key: bytes, data: bytes) -> bytes:
    iv = get_random_bytes(16)
    return iv + AES.new(key, AES.MODE_CBC, iv=iv).encrypt(padding_aes256_cbc(data))


def decrypt_aes256_cbc(key: bytes, data: bytes) -> bytes:
    iv, result_enc = data[:16], data[16:]
    return unpadding_aes256_cbc(AES.new(key, AES.MODE_CBC, iv=iv).decrypt(result_enc))
