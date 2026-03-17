from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs
import base64
import shlex
import json


class CurlParserError(ValueError):
    pass

@dataclass
class ParsedCurl:
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, str] = field(default_factory=dict)
    body: dict | None = None
    auth: dict | None = None
    timeout: int | None = None

def parse_curl(curl_string: str) -> ParsedCurl:
    if not curl_string.strip():
        raise CurlParserError("Empty curl command")

    tokens = shlex.split(curl_string)

    if tokens[0] == "curl":
        tokens = tokens[1:]

    method = None
    url = None
    headers = {}
    params = {}
    auth = None
    body = None
    body_string = None
    timeout = None

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token in ("-X", "--request"):
            method = tokens[i + 1]
            i += 2

        elif token.startswith(("http://", "https://")):
            url = token
            i += 1

        elif token in ("-H", "--header"):
            header = tokens[i + 1]
            spl_header = header.split(": ", 1)
            headers[spl_header[0]] = spl_header[1]
            i += 2

        elif token in ("-u", "--user"):
            auth_token = tokens[i + 1]
            spl_auth_token = auth_token.split(":", 1)
            username = spl_auth_token[0]
            password = spl_auth_token[1]
            auth = {"type": "basic", "username": username, "password": password}
            i += 2

        elif token in ("-d", "--data", "--data-raw"):
            body_string = tokens[i + 1]
            i += 2

        elif token in ("-m", "--max-time"):
            timeout = int(tokens[i + 1])
            i += 2

        else:
            i += 1

    if url is None:
        raise CurlParserError("No URL found in curl command")

    if method is None:
        if body_string is not None:
            method = "POST"
        else:
            method = "GET"

    parsed_url = urlparse(url)
    parsed_query_str = parse_qs(parsed_url.query)
    qs_dict = {k: v[0] for k, v in parsed_query_str.items()}
    bare_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    url = bare_url
    params = qs_dict

    auth_header = headers.get("Authorization", "")
    if auth_header:
        del headers["Authorization"]
        if auth_header.startswith("Bearer"):
            spl_token = auth_header.split(" ")[1]
            auth = {"type": "bearer", "token": spl_token}
        elif auth_header.startswith("Basic"):
            spl_token = auth_header.split(" ")[1]
            decoded = base64.b64decode(spl_token).decode("utf-8")
            username, password = decoded.split(":", 1)
            auth = {"type": "basic", "username": username, "password": password}

    if body_string is not None:
        content_type = headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                parsed = json.loads(body_string)
                body = {"json": parsed}
            except json.decoder.JSONDecodeError:
                body = {"raw": body_string}
        else:
            body = {"raw": body_string}

    return ParsedCurl(method=method, url=url, headers=headers, params=params, auth=auth, body=body, timeout=timeout)