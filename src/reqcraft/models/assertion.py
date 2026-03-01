from __future__ import annotations
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field
from enum import Enum

class Op(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"
    MATCHES = "matches"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"

class StatusAssertion(BaseModel):
    type: Literal["status"]
    expected: int

class JsonAssertion(BaseModel):
    type: Literal["json"]
    path: str
    op: Op
    expected: object = None

class HeaderAssertion(BaseModel):
    type: Literal["header"]
    name: str
    op: Op
    expected: str = ""

class ResponseTimeAssertion(BaseModel):
    type: Literal["response_time"]
    op: Op
    expected: int

class BodySizeAssertion(BaseModel):
    type: Literal["body_size"]
    op: Op
    expected: int

Assertion = Annotated[
    Union[StatusAssertion, JsonAssertion, HeaderAssertion, ResponseTimeAssertion, BodySizeAssertion],
    Field(discriminator="type")
]