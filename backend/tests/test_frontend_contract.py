import re
from pathlib import Path

from app.main import app

FUNCTION_PATTERN = re.compile(
    r"export function\s+(?P<name>\w+)\([^)]*\)\s*\{"
    r"(?P<body>.*?)(?=\nexport function|\Z)",
    re.DOTALL,
)
METHOD_PATTERN = re.compile(r'method:\s*["\'](?P<method>\w+)["\']')
URL_PATTERN = re.compile(
    r"url:\s*(?P<expression>.*?),\s*\n\s*method:",
    re.DOTALL,
)
PATH_PARAMETER_PATTERN = re.compile(r"\{[^}]+\}")


def _parse_frontend_url(expression: str) -> tuple[str, set[str]]:
    template = re.match(r"`(?P<url>[^`]+)`", expression)
    concatenated_path = re.match(
        r'["\'](?P<url>[^"\']+)["\']\s*\+\s*(?P<parameter>\w+)',
        expression,
    )
    literal = re.match(r'["\'](?P<url>[^"\']+)["\']', expression)

    if template:
        url = re.sub(r"\$\{([^}]+)\}", r"{\1}", template.group("url"))
    elif concatenated_path and "?" not in concatenated_path.group("url"):
        url = (
            concatenated_path.group("url")
            + "{"
            + concatenated_path.group("parameter")
            + "}"
        )
    elif literal:
        url = literal.group("url")
    else:
        raise AssertionError(f"Unsupported frontend URL expression: {expression}")

    # Query fragments may be split across several concatenated JS strings.
    literal_fragments = "".join(re.findall(r'["\']([^"\']*)["\']', expression))
    query_parameters = set(re.findall(r"[?&](\w+)=", literal_fragments))
    return f"/api{url.split('?', 1)[0]}", query_parameters


def _frontend_operations() -> list[tuple[str, str, str, set[str]]]:
    service_file = (
        Path(__file__).resolve().parents[2]
        / "frontend"
        / "src"
        / "service"
        / "apis.js"
    )
    source = service_file.read_text(encoding="utf-8")
    exported_names = set(re.findall(r"export function\s+(\w+)\(", source))
    operations = []

    for function_match in FUNCTION_PATTERN.finditer(source):
        name = function_match.group("name")
        body = function_match.group("body")
        method_match = METHOD_PATTERN.search(body)
        url_match = URL_PATTERN.search(body)
        assert method_match is not None, f"Could not parse method for {name}"
        assert url_match is not None, f"Could not parse URL for {name}"
        path, query_parameters = _parse_frontend_url(
            url_match.group("expression").strip()
        )
        operations.append(
            (name, method_match.group("method").lower(), path, query_parameters)
        )

    assert {operation[0] for operation in operations} == exported_names
    return operations


def _canonical_path(path: str) -> str:
    # Frontend variable names and FastAPI parameter names need not be identical.
    return PATH_PARAMETER_PATTERN.sub("{parameter}", path)


def test_legacy_vue_api_calls_exist_in_openapi() -> None:
    schema = app.openapi()
    backend_operations = {
        (method, _canonical_path(path)): operation
        for path, path_item in schema["paths"].items()
        for method, operation in path_item.items()
        if method in {"get", "post", "put", "patch", "delete"}
    }

    for name, method, path, expected_query_parameters in _frontend_operations():
        operation = backend_operations.get((method, _canonical_path(path)))
        assert operation is not None, (
            f"Frontend function {name} calls missing operation "
            f"{method.upper()} {path}"
        )
        actual_query_parameters = {
            parameter["name"]
            for parameter in operation.get("parameters", [])
            if parameter["in"] == "query"
        }
        assert expected_query_parameters <= actual_query_parameters, (
            f"Frontend function {name} expects missing query parameters: "
            f"{expected_query_parameters - actual_query_parameters}"
        )
