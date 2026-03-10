import httpx
import respx
import pytest
from reqcraft.models.collection import Collection, Request, Method
from reqcraft.models.assertion import StatusAssertion
from reqcraft.models.collection import Extract
from reqcraft.core.executor import execute, _sort_requests


def make_collection(requests: list[Request], variables: dict[str, str] = {}) -> Collection:
    return Collection(name="test", variables=variables, requests=requests)


def make_request(**kwargs) -> Request:
    defaults = {"id": "req1", "name": "Test Request", "method": Method.GET, "url": "https://test.com"}
    defaults.update(kwargs)
    return Request(**defaults)


def test_execute_basic_request():
    with respx.mock:
        respx.get("https://test.com").mock(return_value=httpx.Response(200))
        report = execute(
            make_collection([make_request()]),
            variables={}, only=[], skip=[], fail_fast=False, verbose=False,
        )

    assert report.total == 1
    assert report.passed == 1
    assert report.failed == 0


def test_execute_variables_substituted_in_url():
    with respx.mock:
        respx.get("https://api.example.com/users").mock(return_value=httpx.Response(200))
        report = execute(
            make_collection(
                [make_request(url="{{ base_url }}/users")],
                variables={"base_url": "https://api.example.com"},
            ),
            variables={}, only=[], skip=[], fail_fast=False, verbose=False,
        )

    assert report.total == 1
    assert report.passed == 1


def test_execute_cli_vars_override_collection_vars():
    with respx.mock:
        respx.get("https://override.com/users").mock(return_value=httpx.Response(200))
        report = execute(
            make_collection(
                [make_request(url="{{ base_url }}/users")],
                variables={"base_url": "https://original.com"},
            ),
            variables={"base_url": "https://override.com"},
            only=[], skip=[], fail_fast=False, verbose=False,
        )

    assert report.total == 1
    assert report.passed == 1


def test_execute_assertion_failure_recorded():
    with respx.mock:
        respx.get("https://test.com").mock(return_value=httpx.Response(404))
        req = make_request(assertions=[StatusAssertion(type="status", expected=200)])
        report = execute(
            make_collection([req]),
            variables={}, only=[], skip=[], fail_fast=False, verbose=False,
        )

    assert report.failed == 1
    assert report.results[0].passed is False
    assert report.results[0].assertions[0].passed is False


def test_execute_fail_fast_stops_after_first_failure():
    with respx.mock:
        respx.get("https://test.com/a").mock(return_value=httpx.Response(500))
        respx.get("https://test.com/b").mock(return_value=httpx.Response(200))
        req_a = make_request(id="a", url="https://test.com/a", assertions=[StatusAssertion(type="status", expected=200)])
        req_b = make_request(id="b", url="https://test.com/b")
        report = execute(
            make_collection([req_a, req_b]),
            variables={}, only=[], skip=[], fail_fast=True, verbose=False,
        )

    assert report.failed == 1
    assert report.skipped == 1
    assert len(report.results) == 1


def test_execute_timeout_recorded_as_failed():
    with respx.mock:
        respx.get("https://test.com").mock(side_effect=httpx.TimeoutException("timed out"))
        report = execute(
            make_collection([make_request()]),
            variables={}, only=[], skip=[], fail_fast=False, verbose=False,
        )

    assert report.failed == 1
    assert report.results[0].passed is False
    assert report.results[0].error is not None
    assert report.results[0].status_code is None


def test_execute_only_flag_runs_subset():
    with respx.mock:
        respx.get("https://test.com/a").mock(return_value=httpx.Response(200))
        req_a = make_request(id="a", url="https://test.com/a")
        req_b = make_request(id="b", url="https://test.com/b")
        report = execute(
            make_collection([req_a, req_b]),
            variables={}, only=["a"], skip=[], fail_fast=False, verbose=False,
        )

    assert report.total == 1
    assert report.results[0].request_id == "a"


def test_execute_only_flag_includes_dependencies():
    with respx.mock:
        respx.get("https://test.com/login").mock(return_value=httpx.Response(200))
        respx.get("https://test.com/profile").mock(return_value=httpx.Response(200))
        req_login = make_request(id="login", url="https://test.com/login")
        req_profile = make_request(id="profile", url="https://test.com/profile", depends_on=["login"])
        req_other = make_request(id="other", url="https://test.com/other")
        report = execute(
            make_collection([req_login, req_profile, req_other]),
            variables={}, only=["profile"], skip=[], fail_fast=False, verbose=False,
        )

    assert report.total == 2
    ids = [r.request_id for r in report.results]
    assert "login" in ids
    assert "profile" in ids
    assert "other" not in ids


def test_execute_skip_flag_excludes_request():
    with respx.mock:
        respx.get("https://test.com/b").mock(return_value=httpx.Response(200))
        req_a = make_request(id="a", url="https://test.com/a")
        req_b = make_request(id="b", url="https://test.com/b")
        report = execute(
            make_collection([req_a, req_b]),
            variables={}, only=[], skip=["a"], fail_fast=False, verbose=False,
        )

    assert report.total == 1
    assert report.results[0].request_id == "b"


def test_execute_skip_dependency_raises():
    req_a = make_request(id="a", url="https://test.com/a")
    req_b = make_request(id="b", url="https://test.com/b", depends_on=["a"])

    with pytest.raises(ValueError, match="Cannot skip"):
        execute(
            make_collection([req_a, req_b]),
            variables={}, only=[], skip=["a"], fail_fast=False, verbose=False,
        )


def test_execute_extracted_value_used_in_next_request():
    with respx.mock:
        respx.post("https://test.com/login").mock(
            return_value=httpx.Response(200, json={"token": "secret123"})
        )
        respx.get("https://test.com/profile").mock(return_value=httpx.Response(200))

        req_login = make_request(
            id="login",
            method=Method.POST,
            url="https://test.com/login",
            extract=[Extract(name="auth_token", source="body", path="token")],
        )
        req_profile = make_request(
            id="profile",
            url="https://test.com/profile",
            headers={"Authorization": "Bearer {{ auth_token }}"},
            depends_on=["login"],
        )
        report = execute(
            make_collection([req_login, req_profile]),
            variables={}, only=[], skip=[], fail_fast=False, verbose=False,
        )

    assert report.passed == 2
    profile_result = next(r for r in report.results if r.request_id == "profile")
    assert profile_result.request_headers["Authorization"] == "Bearer secret123"


def test_sort_requests_respects_depends_on():
    req_a = make_request(id="a", url="https://test.com", depends_on=["b"])
    req_b = make_request(id="b", url="https://test.com")

    sorted_reqs = _sort_requests([req_a, req_b])
    ids = [r.id for r in sorted_reqs]

    assert ids.index("b") < ids.index("a")
