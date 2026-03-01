from pathlib import Path
import yaml
from reqcraft.models.collection import Collection
from reqcraft.models.environment import Environment

def load_collection(collection_path: Path) -> Collection:
    with open(collection_path, 'r') as stream:
        content = yaml.safe_load(stream)

    return Collection.model_validate(content)

def load_environment(env_path: Path) -> Environment:
    with open(env_path, 'r') as stream:
        content = yaml.safe_load(stream)

    return Environment.model_validate(content)