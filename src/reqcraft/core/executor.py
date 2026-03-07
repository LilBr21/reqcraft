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


def _collect_with_deps(ids: set[str], by_id: dict[str, Request]) -> set[str]:
    result: set[str] = set()

    def visit(req_id: str) -> None:
        if req_id in result:
            return
        result.add(req_id)
        for dep_id in by_id[req_id].depends_on:
            visit(dep_id)

    for req_id in ids:
        visit(req_id)

    return result


def execute(collection: Collection, variables: dict[str, str], only: list[str], skip: list[str],
            fail_fast: bool) -> RunReport:
    final_variables = collection.variables | variables
    sorted_requests = _sort_requests(collection.requests)
    results: list[RequestResult] = []
    passed = 0
    failed = 0

    if only:
        by_id = {r.id: r for r in sorted_requests}
        required_ids = _collect_with_deps(set(only), by_id)
        sorted_requests = [r for r in sorted_requests if r.id in required_ids]

    if skip:
        skip_set = set(skip)
        for r in sorted_requests:
            if r.id not in skip_set:
                blocked = skip_set.intersection(r.depends_on)
                if blocked:
                    raise ValueError(
                        f"Cannot skip '{next(iter(blocked))}' because request '{r.id}' depends on it."
                    )
        sorted_requests = [r for r in sorted_requests if r.id not in skip_set]

    for req in sorted_requests:
        assertions_passed = True
        assertion_results = []
        url = render(req.url, final_variables)
        headers = {k: render(v, final_variables) for k, v in req.headers.items()}
        response = httpx.request(
            req.method.value,
            url,
            headers=headers,
            params=req.params,
            json=req.body.json_body if req.body and req.body.json_body else None,
            data=req.body.form if req.body and req.body.form else None,
            content=req.body.raw if req.body and req.body.raw else None,
        )
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
            if fail_fast:
                return RunReport(
                    total=len(sorted_requests),
                    passed=passed,
                    failed=failed,
                    skipped=len(sorted_requests) - len(results),
                    results=results
                )

    return RunReport(
        total=len(sorted_requests),
        passed=passed,
        failed=failed,
        results=results
    )

def execute_dry_run(collection: Collection, variables: dict[str, str]) -> None:
    final_variables = collection.variables | variables
    sorted_requests = _sort_requests(collection.requests)

    for req in sorted_requests:
        try:
            url = render(req.url, final_variables)
            headers = {k: render(v, final_variables) for k, v in req.headers.items()}
        except Exception as e:
            raise ValueError(f"Render error in request '{req.id}': {e}")

        print(f"{req.method.value} {url}")
        for key, value in headers.items():
            print(f"  {key}: {value}")
        if req.body:
            if req.body.json_body:
                print(f"  body (json): {req.body.json_body}")
            elif req.body.form:
                print(f"  body (form): {req.body.form}")
            elif req.body.raw:
                print(f"  body (raw): {req.body.raw}")
        print()

