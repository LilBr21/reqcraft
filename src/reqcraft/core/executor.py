import httpx
from reqcraft.core.renderer import render
from reqcraft.core.extractor import extract_values
from reqcraft.core.assertions import evaluate
from reqcraft.models.collection import Collection, Request
from reqcraft.models.result import RequestResult, RunReport

def _sort_requests(requests: list[Request]) -> list[Request]:
    result: list[Request] = []
    visited: set[str] = set()
    by_id = {req.id: req for req in requests}

    def visit(request: Request):
            if request.id in visited:
                return
            for dep_id in request.depends_on:
                visit(by_id[dep_id])
            visited.add(request.id)
            result.append(request)

    for req in requests:
        visit(req)

    return result

def execute(collection: Collection, variables: dict[str, str]) -> RunReport:
    final_variables = collection.variables | variables
    sorted_requests = _sort_requests(collection.requests)
    results: list[RequestResult] = []
    passed = 0
    failed = 0

    for req in sorted_requests:
        assertions_passed = True
        assertion_results = []
        url = render(req.url, final_variables)
        headers = {k: render(v, final_variables) for k, v in req.headers.items()}
        response = httpx.request(req.method.value, url, headers=headers, params=req.params)
        for assertion in req.assertions:
            evaluated = evaluate(assertion, response)
            if not evaluated.passed:
                assertions_passed = False
            assertion_results.append(evaluated)
        extracted = extract_values(response, req.extract)
        if extracted:
            final_variables.update(extracted)
        results.append(RequestResult(
            request_id=req.id,
            name=req.name,
            passed=assertions_passed,
            status_code=response.status_code,
            response_time_ms=response.elapsed.total_seconds() * 1000,
            assertions=assertion_results,
            body=response.text,
            error=None
        ))
        if assertions_passed:
            passed += 1
        else:
            failed += 1

    return RunReport(
        total=len(sorted_requests),
        passed=passed,
        failed=failed,
        results=results
    )