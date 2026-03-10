from __future__ import annotations
from typing import Literal, TypeAlias, Annotated, Union
from pydantic import BaseModel, Field
from enum import Enum
from reqcraft.models.assertion import Assertion

class Method(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

class AuthType(str, Enum):
    BEARER = "bearer"
    BASIC = "basic"
    API_KEY = "api_key"

class BearerAuth(BaseModel):
    type: Literal[AuthType.BEARER]
    token: str

class BasicAuth(BaseModel):
    type: Literal[AuthType.BASIC]
    username: str
    password: str

class ApiKeyAuth(BaseModel):
    type: Literal[AuthType.API_KEY]
    header: str
    value: str

Auth: TypeAlias = Annotated[
    Union[BasicAuth, BearerAuth, ApiKeyAuth],
    Field(discriminator="type"),
]

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
    auth: Auth | None = None
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