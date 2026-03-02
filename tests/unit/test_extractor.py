import httpx
import respx
from reqcraft.models.collection import Extract
from reqcraft.core.extractor import extract_values


def test_extract_from_body():
    with respx.mock:
        respx.post("https://test.com/login").mock(
            return_value=httpx.Response(200, json={"data": {"token": "abc123"}})
        )
        response = httpx.post("https://test.com/login")

    extracts = [Extract(name="auth_token", source="body", path="data.token")]
    result = extract_values(response, extracts)

    assert result == {"auth_token": "abc123"}


def test_extract_from_header():
    with respx.mock:
        respx.get("https://test.com").mock(
            return_value=httpx.Response(200, headers={"x-request-id": "req-42"})
        )
        response = httpx.get("https://test.com")

    extracts = [Extract(name="request_id", source="header", path="x-request-id")]
    result = extract_values(response, extracts)

    assert result == {"request_id": "req-42"}


def test_extract_status():
    with respx.mock:
        respx.get("https://test.com").mock(return_value=httpx.Response(201))
        response = httpx.get("https://test.com")

    extracts = [Extract(name="status", source="status")]
    result = extract_values(response, extracts)

    assert result == {"status": "201"}


def test_extract_multiple():
    with respx.mock:
        respx.post("https://test.com/login").mock(
            return_value=httpx.Response(200, json={"token": "xyz", "user_id": 7})
        )
        response = httpx.post("https://test.com/login")

    extracts = [
        Extract(name="token", source="body", path="token"),
        Extract(name="user_id", source="body", path="user_id"),
    ]
    result = extract_values(response, extracts)

    assert result == {"token": "xyz", "user_id": "7"}


def test_extract_empty_list():
    with respx.mock:
        respx.get("https://test.com").mock(return_value=httpx.Response(200))
        response = httpx.get("https://test.com")

    result = extract_values(response, [])

    assert result == {}
