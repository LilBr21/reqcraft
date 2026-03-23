import yaml
from reqcraft.core.curl_parser import ParsedCurl
from reqcraft.models.collection import Collection, AuthType, BearerAuth, BasicAuth, RequestBody, Request, Method, ApiKeyAuth
from urllib.parse import urlparse

def remove_empty(d):
    if isinstance(d, dict):
        return {k: remove_empty(v) for k, v in d.items() if v not in (None, {}, [])}
    if isinstance(d, list):
        return [remove_empty(item) for item in d]
    return d

def parsed_curl_to_collection(curl: ParsedCurl, collection_name: str | None = None, api_key_header: str | None = None) -> Collection:
    name = ""
    auth = None
    body = None

    parsed_url = urlparse(curl.url)
    req_id = f"{curl.method.lower()}-{parsed_url.path.strip('/').replace('/', '-').lower()}"
    req_name = f"{curl.method} {parsed_url.path}"

    if collection_name is None:
        netloc = parsed_url.netloc
        name = netloc + " import"
    else:
        name = collection_name

    if curl.auth:
        if curl.auth.get("type") == AuthType.BEARER:
            auth = BearerAuth(type = AuthType.BEARER, token = curl.auth.get("token", ""))
        elif curl.auth.get("type") == AuthType.BASIC:
            auth = BasicAuth(type = AuthType.BASIC, username = curl.auth.get("username", ""), password=curl.auth.get("password", ""))
        else:
            auth = None

    if api_key_header and curl.headers.get(api_key_header):
        header_value = curl.headers.get(api_key_header)
        auth = ApiKeyAuth(type = AuthType.API_KEY, header = api_key_header, value = header_value)
        del(curl.headers[api_key_header])

    if curl.body:
        if curl.body.get("json"):
            body = RequestBody(json = curl.body.get("json"))
        else:
            body = RequestBody(json = None, raw = curl.body.get("raw"))

    request = Request(
        id = req_id,
        name = req_name,
        method = Method(curl.method),
        url = curl.url,
        headers = curl.headers,
        params = curl.params,
        auth = auth,
        body = body,
        timeout = curl.timeout if curl.timeout is not None else 30,
    )

    return Collection(
        name=name,
        requests=[request],
    )

def collection_to_yaml(collection: Collection) -> str:
    data = collection.model_dump(by_alias=True, exclude_none=True, mode="json")
    return yaml.dump(remove_empty(data), default_flow_style=False, allow_unicode=True, sort_keys=False)