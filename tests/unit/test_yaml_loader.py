import pytest
from pathlib import Path
from reqcraft.utils.yaml_loader import load_collection, load_environment


def test_load_valid_collection(tmp_path: Path):
    f = tmp_path / "collection.yaml"
    f.write_text("""
name: My Collection
requests:
  - id: get-users
    name: Get Users
    url: https://api.example.com/users
""")
    collection = load_collection(f)

    assert collection.name == "My Collection"
    assert len(collection.requests) == 1
    assert collection.requests[0].id == "get-users"


def test_load_collection_with_variables(tmp_path: Path):
    f = tmp_path / "collection.yaml"
    f.write_text("""
name: Vars Collection
variables:
  base_url: https://api.example.com
  api_key: secret
requests:
  - id: get-users
    url: "{{ base_url }}/users"
""")
    collection = load_collection(f)

    assert collection.variables["base_url"] == "https://api.example.com"
    assert collection.variables["api_key"] == "secret"


def test_load_collection_default_timeout(tmp_path: Path):
    f = tmp_path / "collection.yaml"
    f.write_text("""
name: Test
requests:
  - id: req1
    url: https://test.com
""")
    collection = load_collection(f)

    assert collection.requests[0].timeout == 30


def test_load_collection_custom_timeout(tmp_path: Path):
    f = tmp_path / "collection.yaml"
    f.write_text("""
name: Test
requests:
  - id: req1
    url: https://test.com
    timeout: 5
""")
    collection = load_collection(f)

    assert collection.requests[0].timeout == 5


def test_load_collection_file_not_found():
    with pytest.raises(ValueError, match="File not found"):
        load_collection(Path("/nonexistent/path/collection.yaml"))


def test_load_collection_invalid_yaml(tmp_path: Path):
    f = tmp_path / "bad.yaml"
    f.write_text("name: [unclosed bracket")

    with pytest.raises(ValueError, match="Invalid YAML"):
        load_collection(f)


def test_load_collection_invalid_schema(tmp_path: Path):
    f = tmp_path / "collection.yaml"
    f.write_text("""
name: Bad Collection
requests:
  - id: req1
    url: 12345
    method: INVALID_METHOD
""")
    with pytest.raises(ValueError):
        load_collection(f)


def test_load_valid_environment(tmp_path: Path):
    f = tmp_path / "env.yaml"
    f.write_text("""
name: staging
variables:
  base_url: https://staging.example.com
  api_key: staging-key
""")
    env = load_environment(f)

    assert env.name == "staging"
    assert env.variables["base_url"] == "https://staging.example.com"


def test_load_environment_file_not_found():
    with pytest.raises(ValueError, match="File not found"):
        load_environment(Path("/nonexistent/env.yaml"))
