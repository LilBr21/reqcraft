from __future__ import annotations
from pydantic import BaseModel

class AssertionResult(BaseModel):
    passed: bool
    message: str

class RequestResult(BaseModel):
    request_id: str
    name: str
    passed: bool
    status_code: int | None = None
    response_time_ms: float | None = None
    assertions: list[AssertionResult] = []
    request_url: str | None = None
    request_method: str | None = None
    request_headers: dict[str, str] | None = None
    response_headers: dict[str, str] | None = None
    body: str | None = None
    error: str | None = None

class RunReport(BaseModel):
    total: int
    passed: int
    failed: int
    skipped: int = 0
    results: list[RequestResult]