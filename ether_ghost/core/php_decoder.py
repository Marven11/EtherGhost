import base64
import json
import shutil
import typing as t
from pathlib import Path
from . import custom_encoders
from ..utils.nodejs_bridge import nodejs_eval
from ..utils import const


class Decoder(t.TypedDict):
    type: t.Literal["builtin", "antsword", "custom"]
    phpcode: str  # 在加载失败时为空字符串
    decode_response: t.Callable[[str], str]


decoders: t.Dict[str, Decoder] = {
    "raw": {
        "type": "builtin",
        "phpcode": "function decoder_echo_raw($s) {echo $s;}",
        "decode_response": lambda x: x,
    },
    "base64": {
        "type": "builtin",
        "phpcode": "function decoder_echo_raw($s) {echo base64_encode($s);}",
        "decode_response": lambda x: base64.b64decode(x).decode("utf-8"),
    },
}


def get_antsword_decoder(filepath: Path) -> Decoder:
    if shutil.which("node") is not None:
        asenc = nodejs_eval(
            """
            var decoder = require(FILEPATH);
            console.log(JSON.stringify(decoder.asoutput()));
            """.replace(
                "FILEPATH", repr(filepath.as_posix())
            ),
            [],
        )
        asenc = json.loads(asenc)
        phpcode = asenc + "\nfunction decoder_echo_raw($s) {echo asenc($s);}"
    else:
        phpcode = ""

    def decode_response(text: str):
        return base64.b64decode(
            nodejs_eval(
                """
                var decoder = require(FILEPATH);
                var code = JSON.parse(process.argv[2]);
                console.log(decoder.decode_buff(code).toString('base64'));
                """.replace(
                    "FILEPATH", repr(filepath.as_posix())
                ),
                [json.dumps(text)],
            )
        ).decode()

    return {"type": "antsword", "phpcode": phpcode, "decode_response": decode_response}


def get_custom_decoder(filename: str) -> Decoder:
    phpcode, decode_response = custom_encoders.get_decoder(filename)
    return {
        "type": "custom",
        "phpcode": phpcode,
        "decode_response": decode_response,
    }


for decoder_file in const.ANTSWORD_DECODER_FOLDER.glob("*.js"):
    decoders[f"[AntSword] {decoder_file.name}"] = get_antsword_decoder(decoder_file)


for custom_decoder in custom_encoders.list_custom_decoders():
    decoders[f"[Custom] {custom_decoder}"] = get_custom_decoder(custom_decoder)
