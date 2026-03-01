import re
import jmespath
import httpx
from reqcraft.models.assertion import Assertion, Op
from reqcraft.models.result import AssertionResult

def _apply_op(op: Op, actual, expected) -> bool:
    if op == Op.EQUALS:
        return expected == actual
    elif op == Op.NOT_EQUALS:
        return expected != actual
    elif op == Op.CONTAINS:
        return expected in actual
    elif op == Op.EXISTS:
        return actual is not None
    elif op == Op.NOT_EXISTS:
        return actual is None
    elif op == Op.MATCHES:
        return bool(re.fullmatch(expected, str(actual)))
    elif op == Op.GREATER_THAN:
        return actual > expected
    elif op == Op.LESS_THAN:
        return actual < expected
    else:
        return False

def evaluate(assertion: Assertion, response: httpx.Response) -> AssertionResult:
    if assertion.type == "status":
        passed = assertion.expected == response.status_code
        success_message = f"✓ status == {assertion.expected}"
        error_message = f"✗ status expected {assertion.expected}, got {response.status_code}"
        message = success_message if passed else error_message
        return AssertionResult(passed=passed, message=message)

    elif assertion.type == "json":
        value = jmespath.search(assertion.path, response.json())

        passed = _apply_op(assertion.op, value, assertion.expected)
        success_message = f"✓ json {assertion.path} {assertion.op.value} {assertion.expected}"
        error_message = f"✗ json {assertion.path}: expected {assertion.expected}, got {value}"
        message = success_message if passed else error_message
        return AssertionResult(passed=passed, message=message)

    elif assertion.type == "header":
        value = response.headers.get(assertion.name)

        passed = _apply_op(assertion.op, value, assertion.expected)
        success_message = f"✓ header '{assertion.name}' {assertion.op.value} '{assertion.expected}'"
        error_message = f"✗ header '{assertion.name}': expected '{assertion.expected}', got '{value}'"
        message = success_message if passed else error_message
        return AssertionResult(passed=passed, message=message)

    elif assertion.type == "response_time":
        value =  response.elapsed.total_seconds() * 1000

        passed = _apply_op(assertion.op, value, assertion.expected)
        success_message = f"✓ response_time {assertion.op.value} {assertion.expected}ms"
        error_message = f"✗ response_time: expected {assertion.op.value} {assertion.expected}ms, got {value:.1f}ms"
        message = success_message if passed else error_message
        return AssertionResult(passed=passed, message=message)

    elif assertion.type == "body_size":
        value = len(response.content)

        passed = _apply_op(assertion.op, value, assertion.expected)
        success_message = f"✓ body_size {assertion.op.value} {assertion.expected}"
        error_message = f"✗ body_size: expected {assertion.op.value} {assertion.expected}, got {value}"
        message = success_message if passed else error_message
        return AssertionResult(passed=passed, message=message)

    else:
        return AssertionResult(passed=False, message="Failed")
