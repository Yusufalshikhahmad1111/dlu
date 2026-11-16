from __future__ import annotations

import ast
from pathlib import Path
import re
import sys


FILES = (Path("dlu_app/ui.py"), Path("dlu_app/call_ui.py"))


def main() -> int:
    errors: list[str] = []

    for path in FILES:
        text = path.read_text(encoding="utf-8")
        if re.search(r"#[0-9a-fA-F]{6}", text):
            errors.append(f"{path}: hardcoded hex/design color literal found")

        tree = ast.parse(text, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "QFont":
                    errors.append(f"{path}:{node.lineno}: direct QFont construction")

        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if fn.name in {"show_module", "draw_port_grid", "draw_full_module_slot"}:
                    for child in ast.walk(fn):
                        if isinstance(child, ast.Attribute):
                            if child.value.id == "slot" if isinstance(child.value, ast.Name) else False:
                                errors.append(
                                    f"{path}:{child.lineno}: mixed slot attribute access "
                                    f"in {fn.name}: slot.{child.attr}"
                                )

        if re.search(r"QColor\(\s*\{[A-Z_]+\}\s*\)", text):
            errors.append(f"{path}: palette placeholder passed to QColor")

    if errors:
        for error in errors:
            print(error)
        return 1

    print("UI static audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
