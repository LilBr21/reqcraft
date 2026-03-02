from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field
from enum import Enum
from reqcraft.models.assertion import Assertion

class Method(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

class Extract(BaseModel):
    name: str
    source: Literal["body", "header", "status"]
    path: str = ""

class RequestBody(BaseModel):
    json_body: dict[str, object] | None = Field(None, alias="json")
    form: dict[str, str] | None = None
    raw: str | None = None

    model_config = {"populate_by_name": True}

class Request(BaseModel):
    id: str
    name: str = ""
    method: Method = Method.GET
    url: str
    headers: dict[str, str] = {}
    params: dict[str, str] = {}
    body: RequestBody | None = None
    timeout: int = 30
    depends_on: list[str] = []
    assertions: list[Assertion] = []
    extract: list[Extract] = []

class Collection(BaseModel):
    name: str
    version: str = "1.0"
    variables: dict[str, str] = {}
    imports: list[str] = []
    requests: list[Request] = []