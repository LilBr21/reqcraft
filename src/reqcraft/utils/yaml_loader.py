from pathlib import Path
import yaml
from reqcraft.models.collection import Collection
from reqcraft.models.environment import Environment

def load_collection(collection_path: Path) -> Collection:
    try:
        with open(collection_path, 'r') as stream:
            content = yaml.safe_load(stream)
            return Collection.model_validate(content)
    except FileNotFoundError:
        raise ValueError(f"File not found: {collection_path}")
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {collection_path}: {exc}")
    except Exception as exc:
        raise ValueError(f"Collection error: {exc}")

def load_environment(env_path: Path) -> Environment:
    try:
        with open(env_path, 'r') as stream:
            content = yaml.safe_load(stream)
            return Environment.model_validate(content)
    except FileNotFoundError:
        raise ValueError(f"File not found: {env_path}")
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {env_path}: {exc}")
    except Exception as exc:
        raise ValueError(f"Environment error: {exc}")
