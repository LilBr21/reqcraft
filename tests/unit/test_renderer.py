import pytest
from jinja2 import UndefinedError
from reqcraft.core.renderer import render


def test_render_single_variable():
    result = render("Hello {{ name }}", {"name": "world"})
    assert result == "Hello world"


def test_render_multiple_variables():
    result = render("{{ method }} {{ base_url }}/users", {"method": "GET", "base_url": "https://api.com"})
    assert result == "GET https://api.com/users"


def test_render_no_variables():
    result = render("https://api.com/users", {})
    assert result == "https://api.com/users"


def test_render_raises_on_missing_variable():
    with pytest.raises(UndefinedError):
        render("{{ missing }}", {})


def test_render_url_with_variable():
    result = render("{{ base_url }}/posts/{{ post_id }}", {"base_url": "https://api.com", "post_id": "42"})
    assert result == "https://api.com/posts/42"
