from __future__ import annotations
from pydantic import BaseModel

class Variable(BaseModel):
    value: str
    description: str = ""

class Environment(BaseModel):
    name: str
    variables: dict[str, str]