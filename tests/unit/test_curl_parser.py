import pytest

from reqcraft.core.curl_parser import parse_curl, CurlParserError

def test_parse_simple_get():
    result = parse_curl("curl https://api.example.com")
    assert result.method == "GET"
    assert result.url == "https://api.example.com"

def test_explicit_post_with_x():
    result = parse_curl("curl -X POST https://api.example.com  -H 'Authorization: Bearer token123' -H 'Content-Type: application/json' -d '{\"name\": \"Alice\"}'")
    assert result.method == "POST"

def test_body_without_x():
    result = parse_curl(
        "curl https://api.example.com  -H 'Authorization: Bearer token123' -H 'Content-Type: application/json' -d '{\"name\": \"Alice\"}'")
    assert result.method == "POST"

def test_single_header():
    result = parse_curl("curl -X POST https://api.example.com -H 'Content-Type: application/json'")
    assert result.headers["Content-Type"] == "application/json"

def test_bearer_auth():
    result = parse_curl("curl https://api.example.com  -H 'Authorization: Bearer token123'")
    assert "Authorization" not in result.headers
    assert result.auth == {"type": "bearer", "token": "token123"}

def test_basic_auth_from_flag():
    result = parse_curl("curl https://api.example.com -u alice:secret")
    assert result.auth == {"type": "basic", "username": "alice", "password": "secret"}

def test_json_body():
    result = parse_curl("curl -X POST https://api.example.com -H 'Content-Type: application/json' -d '{\"name\": \"Alice\"}'")
    assert result.body == {"json": {"name": "Alice"}}

def test_raw_body():
    result = parse_curl(
        "curl -X POST https://api.example.com -H 'Content-Type: application/json' -d 'hello world'")
    assert result.body == {"raw": "hello world"}

def test_query_params():
    result = parse_curl("curl https://api.example.com?q=foo&limit=10")
    assert result.params == {"q": "foo", "limit": "10"}
    assert result.url == "https://api.example.com"

def test_timeout():
    result = parse_curl("curl https://api.example.com --max-time 10")
    assert result.timeout == 10

def test_empty_string_raises():
    with pytest.raises(CurlParserError):
        parse_curl("")
