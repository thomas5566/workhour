import ast
from pathlib import Path

UNSAFE_SQL_CALLS = {
    "exec_driver_sql",
    "from_statement",
    "literal_column",
    "text",
}


def test_application_code_does_not_use_raw_sql_construction() -> None:
    """Prevent future request data from reaching raw SQL construction APIs."""
    app_root = Path(__file__).parents[1] / "app"
    violations: list[str] = []

    for source_file in app_root.rglob("*.py"):
        tree = ast.parse(source_file.read_text(encoding="utf-8"), source_file)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            function_name = (
                node.func.id
                if isinstance(node.func, ast.Name)
                else node.func.attr
                if isinstance(node.func, ast.Attribute)
                else ""
            )
            if function_name in UNSAFE_SQL_CALLS:
                relative_path = source_file.relative_to(app_root.parent)
                violations.append(f"{relative_path}:{node.lineno} ({function_name})")

    assert violations == [], "Raw SQL construction is not allowed: " + ", ".join(violations)
