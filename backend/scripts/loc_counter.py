#!/usr/bin/env python3
"""
Reproducible Source LOC Counter for Backend Codebase.

Counting Rules (per Section 8):
- Includes production Python source files (e.g., backend/app/).
- Includes automated test source files (e.g., backend/tests/).
- Includes executable backend scripts and migration source files (e.g., backend/scripts/, backend/migrations/).
- Excludes blank lines.
- Excludes standalone comment lines and documentation-only lines (docstrings).
- A nonblank line containing executable code and an inline comment counts once.
- Excludes Markdown, README files, JSON, YAML, lockfiles, Docker instructions, config data.
- Excludes virtual environments, caches, __pycache__, .git, build outputs.
- Categorizes lines into:
  1. Production source LOC
  2. Test source LOC
  3. Other executable backend source LOC (scripts, migrations)
"""

import ast
import io
import json
import os
import sys
import tokenize
from pathlib import Path
from typing import Dict, List, Set, Tuple


EXCLUDED_DIRS: Set[str] = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".mypy_cache",
    ".ruff_cache",
    "htmlcov",
    ".coverage",
    "dist",
    "build",
    "eggs",
    ".eggs",
}

VALID_EXTENSIONS: Set[str] = {".py"}


def extract_docstring_line_numbers(code_text: str) -> Set[int]:
    """Parse AST to identify line ranges that belong strictly to docstrings."""
    docstring_lines: Set[int] = set()
    try:
        tree = ast.parse(code_text)
    except SyntaxError:
        return docstring_lines

    def _mark_docstring_node(node: ast.AST) -> None:
        if (
            isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            expr_stmt = node.body[0]
            start_line = expr_stmt.lineno
            end_line = getattr(expr_stmt, "end_lineno", start_line)
            for lineno in range(start_line, end_line + 1):
                docstring_lines.add(lineno)

    for node in ast.walk(tree):
        _mark_docstring_node(node)

    return docstring_lines


def count_source_lines_in_file(file_path: Path) -> Tuple[int, int, int]:
    """
    Count (code_lines, comment_only_lines, blank_lines) for a Python file.
    Only non-blank, non-comment, non-docstring lines containing code tokens count.
    """
    try:
        with open(file_path, "rb") as f:
            raw_bytes = f.read()
    except (OSError, IOError):
        return 0, 0, 0

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = raw_bytes.decode("latin-1")
        except UnicodeDecodeError:
            return 0, 0, 0

    lines = text.splitlines()
    total_lines = len(lines)
    if total_lines == 0:
        return 0, 0, 0

    docstring_lines = extract_docstring_line_numbers(text)

    # Track line contents via tokenization
    lines_with_code: Set[int] = set()
    lines_with_comment: Set[int] = set()
    lines_with_tokens: Set[int] = set()

    try:
        tokens = tokenize.tokenize(io.BytesIO(raw_bytes).readline)
        for tok in tokens:
            tok_type = tok.exact_type if hasattr(tok, "exact_type") else tok.type
            s_line = tok.start[0]
            e_line = tok.end[0]

            if tok.type in (tokenize.ENCODING, tokenize.NL, tokenize.NEWLINE, tokenize.ENDMARKER):
                continue

            for l_num in range(s_line, e_line + 1):
                lines_with_tokens.add(l_num)

            if tok.type == tokenize.COMMENT:
                for l_num in range(s_line, e_line + 1):
                    lines_with_comment.add(l_num)
            else:
                # Any non-comment, non-whitespace token
                for l_num in range(s_line, e_line + 1):
                    # Check if line is purely in docstrings
                    if l_num not in docstring_lines:
                        lines_with_code.add(l_num)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        # Fallback to conservative line-by-line inspection if tokenize fails
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                lines_with_comment.add(idx)
            elif idx not in docstring_lines:
                lines_with_code.add(idx)

    code_count = len(lines_with_code)
    comment_only_count = 0
    blank_count = 0

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            blank_count += 1
        elif idx in docstring_lines and idx not in lines_with_code:
            comment_only_count += 1
        elif idx in lines_with_comment and idx not in lines_with_code:
            comment_only_count += 1

    return code_count, comment_only_count, blank_count


def classify_file(file_path: Path, backend_root: Path) -> str:
    """Classify file as production, test, or other."""
    rel = file_path.relative_to(backend_root).as_posix()
    if rel.startswith("tests/"):
        return "test"
    elif rel.startswith("app/"):
        return "production"
    else:
        return "other"


def scan_backend_directory(backend_root: Path) -> Dict[str, any]:
    """Scan backend directory and compute verified LOC metrics."""
    results = {
        "production_source_loc": 0,
        "test_source_loc": 0,
        "other_source_loc": 0,
        "total_verified_source_loc": 0,
        "total_files": 0,
        "production_files": 0,
        "test_files": 0,
        "other_files": 0,
        "files_detail": [],
    }

    if not backend_root.exists():
        return results

    for root, dirs, files in os.walk(backend_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]

        for fname in sorted(files):
            ext = Path(fname).suffix.lower()
            if ext not in VALID_EXTENSIONS:
                continue

            fpath = Path(root) / fname
            category = classify_file(fpath, backend_root)
            code_loc, comment_loc, blank_loc = count_source_lines_in_file(fpath)

            rel_path = fpath.relative_to(backend_root).as_posix()
            results["files_detail"].append({
                "path": rel_path,
                "category": category,
                "code_loc": code_loc,
                "comment_loc": comment_loc,
                "blank_loc": blank_loc,
                "total_lines": code_loc + comment_loc + blank_loc,
            })

            results["total_files"] += 1
            if category == "production":
                results["production_source_loc"] += code_loc
                results["production_files"] += 1
            elif category == "test":
                results["test_source_loc"] += code_loc
                results["test_files"] += 1
            else:
                results["other_source_loc"] += code_loc
                results["other_files"] += 1

    results["total_verified_source_loc"] = (
        results["production_source_loc"]
        + results["test_source_loc"]
        + results["other_source_loc"]
    )

    return results


def main() -> None:
    backend_root = Path(__file__).resolve().parent.parent
    if len(sys.argv) > 1 and sys.argv[1] not in ("--json", "--markdown"):
        backend_root = Path(sys.argv[1]).resolve()

    stats = scan_backend_directory(backend_root)

    if "--json" in sys.argv:
        print(json.dumps(stats, indent=2))
        return

    print("=" * 70)
    print("BACKEND VERIFIED SOURCE CODE LINE COUNT REPORT")
    print(f"Backend Root: {backend_root}")
    print("=" * 70)
    print(f"Production Source LOC : {stats['production_source_loc']:>8}  ({stats['production_files']} files)")
    print(f"Test Source LOC       : {stats['test_source_loc']:>8}  ({stats['test_files']} files)")
    print(f"Other Source LOC      : {stats['other_source_loc']:>8}  ({stats['other_files']} files)")
    print("-" * 70)
    print(f"Total Verified LOC    : {stats['total_verified_source_loc']:>8}  ({stats['total_files']} files)")
    print("=" * 70)


if __name__ == "__main__":
    main()
