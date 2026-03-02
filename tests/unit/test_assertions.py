import httpx
import respx
from reqcraft.models.assertion import (
    StatusAssertion, JsonAssertion, HeaderAssertion,
    ResponseTimeAssertion, BodySizeAssertion, Op
)
from reqcraft.core.assertions import evaluate


def test_status_assertion_passes():
    with respx.mock:
        respx.get("https://test.com").mock(return_value=httpx.Response(200))
        response = httpx.get("https://test.com")

    assertion = StatusAssertion(type="status", expected=200)
    result = evaluate(assertion, response)

    assert result.passed is True


def test_status_assertion_fails():
    with respx.mock:
        respx.get("https://test.com").mock(return_value=httpx.Response(404))
        response = httpx.get("https://test.com")

    assertion = StatusAssertion(type="status", expected=200)
    result = evaluate(assertion, response)

    assert result.passed is False


def test_json_equals_passes():
    with respx.mock:
        respx.get("https://test.com").mock(
            return_value=httpx.Response(200, json={"id": 1, "name": "Alice"})
        )
        response = httpx.get("https://test.com")

    assertion = JsonAssertion(type="json", path="id", op=Op.EQUALS, expected=1)
    result = evaluate(assertion, response)

    assert result.passed is True


def test_json_equals_fails():
    with respx.mock:
        respx.get("https://test.com").mock(
            return_value=httpx.Response(200, json={"id": 1, "name": "Alice"})
        )
        response = httpx.get("https://test.com")

    assertion = JsonAssertion(type="json", path="id", op=Op.EQUALS, expected=2)
    result = evaluate(assertion, response)

    assert result.passed is False


def test_json_contains_passes():
    with respx.mock:
        respx.get("https://test.com").mock(
            return_value=httpx.Response(200, json={"full_name": "Alice Cooper"})
        )
        response = httpx.get("https://test.com")

    assertion = JsonAssertion(type="json", path="full_name", op=Op.CONTAINS, expected="Alice")
    result = evaluate(assertion, response)

    assert result.passed is True


def test_json_contains_fails():
    with respx.mock:
        respx.get("https://test.com").mock(
            return_value=httpx.Response(200, json={"full_name": "Alice Cooper"})
        )
        response = httpx.get("https://test.com")

    assertion = JsonAssertion(type="json", path="full_name", op=Op.CONTAINS, expected="Monica")
    result = evaluate(assertion, response)

    assert result.passed is False


def test_json_exists_passes():
    with respx.mock:
        respx.get("https://test.com").mock(
            return_value=httpx.Response(200, json={"token": "abc123"})
        )
        response = httpx.get("https://test.com")

    assertion = JsonAssertion(type="json", path="token", op=Op.EXISTS)
    result = evaluate(assertion, response)

    assert result.passed is True


def test_json_not_exists_passes():
    with respx.mock:
        respx.get("https://test.com").mock(
            return_value=httpx.Response(200, json={"name": "Alice"})
        )
        response = httpx.get("https://test.com")

    assertion = JsonAssertion(type="json", path="missing_field", op=Op.NOT_EXISTS)
    result = evaluate(assertion, response)

    assert result.passed is True


def test_header_assertion_passes():
    with respx.mock:
        respx.get("https://test.com").mock(
            return_value=httpx.Response(200, headers={"content-type": "application/json"})
        )
        response = httpx.get("https://test.com")

    assertion = HeaderAssertion(type="header", name="content-type", op=Op.EQUALS, expected="application/json")
    result = evaluate(assertion, response)

    assert result.passed is True


def test_header_assertion_fails():
    with respx.mock:
        respx.get("https://test.com").mock(
            return_value=httpx.Response(200, headers={"content-type": "text/html"})
        )
        response = httpx.get("https://test.com")

    assertion = HeaderAssertion(type="header", name="content-type", op=Op.EQUALS, expected="application/json")
    result = evaluate(assertion, response)

    assert result.passed is False


def test_body_size_assertion_passes():
    with respx.mock:
        respx.get("https://test.com").mock(
            return_value=httpx.Response(200, content=b"hello")
        )
        response = httpx.get("https://test.com")

    assertion = BodySizeAssertion(type="body_size", op=Op.EQUALS, expected=5)
    result = evaluate(assertion, response)

    assert result.passed is True


def test_body_size_greater_than_passes():
    with respx.mock:
        respx.get("https://test.com").mock(
            return_value=httpx.Response(200, content=b"hello world")
        )
        response = httpx.get("https://test.com")

    assertion = BodySizeAssertion(type="body_size", op=Op.GREATER_THAN, expected=5)
    result = evaluate(assertion, response)

    assert result.passed is True
