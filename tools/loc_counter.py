"""
InfoLens Repository Line of Code (LOC) Counter.
Calculates total lines, source lines of code (SLOC), comments, and blank lines across all domains.
"""

import os
from pathlib import Path

EXTENSIONS = {
    "Python": (".py",),
    "JavaScript/JSX": (".js", ".jsx", ".mjs", ".cjs"),
    "TypeScript/TSX": (".ts", ".tsx"),
    "CSS/HTML": (".css", ".html", ".scss"),
    "JSON/Config": (".json", ".yaml", ".yml", ".toml", ".env", ".example"),
    "Markdown/Docs": (".md", ".rst", ".txt"),
}

EXCLUDED_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".venv",
    "venv",
    "env",
    ".coverage",
    ".idea",
    ".vscode",
    "data",
}


def get_category(path_str: str) -> str:
    path_norm = path_str.replace("\\", "/")
    if path_norm.startswith("ai_engine/"):
        return "AI Engine (ai_engine/)"
    elif path_norm.startswith("tests/"):
        return "AI Engine Tests (tests/)"
    elif path_norm.startswith("backend/tests/"):
        return "Backend Tests (backend/tests/)"
    elif path_norm.startswith("backend/"):
        return "Backend (backend/)"
    elif path_norm.startswith("src/"):
        return "Frontend (src/)"
    else:
        return "Root / Config / Docs"


def count_repository(root_dir: str = "."):
    category_stats = {}
    lang_stats = {}
    total_files = 0
    total_lines = 0
    total_sloc = 0
    total_blank = 0
    total_comment = 0

    for root, dirs, files in os.walk(root_dir):
        # Prune excluded directories in-place
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]
        for f in files:
            fp = Path(root) / f
            rel_p = fp.relative_to(Path(root_dir))
            rel_str = str(rel_p).replace("\\", "/")

            ext = fp.suffix.lower()
            lang = "Other"
            for l_name, exts in EXTENSIONS.items():
                if ext in exts or f in exts or (ext == "" and f.startswith(".")):
                    lang = l_name
                    break

            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as fl:
                    lines = fl.readlines()
                t = len(lines)
                b = sum(1 for l in lines if not l.strip())
                if lang == "Python":
                    c = sum(1 for l in lines if l.strip().startswith("#"))
                elif lang in ("JavaScript/JSX", "TypeScript/TSX", "CSS/HTML"):
                    c = sum(
                        1
                        for l in lines
                        if l.strip().startswith("//")
                        or l.strip().startswith("/*")
                        or l.strip().startswith("*")
                    )
                else:
                    c = 0
                code = t - b - c
                cat = get_category(rel_str)

                total_files += 1
                total_lines += t
                total_sloc += code
                total_blank += b
                total_comment += c

                c_entry = category_stats.setdefault(
                    cat, {"files": 0, "total": 0, "sloc": 0, "blank": 0, "comment": 0}
                )
                c_entry["files"] += 1
                c_entry["total"] += t
                c_entry["sloc"] += code
                c_entry["blank"] += b
                c_entry["comment"] += c

                l_entry = lang_stats.setdefault(
                    lang, {"files": 0, "total": 0, "sloc": 0, "blank": 0, "comment": 0}
                )
                l_entry["files"] += 1
                l_entry["total"] += t
                l_entry["sloc"] += code
                l_entry["blank"] += b
                l_entry["comment"] += c
            except Exception:
                pass

    print("=" * 86)
    print(f"{'Category':38} | {'Files':>6} | {'Total':>8} | {'SLOC':>8} | {'Blank':>6} | {'Comment':>7}")
    print("=" * 86)
    for cat, st in sorted(category_stats.items()):
        print(f"{cat:38} | {st['files']:6d} | {st['total']:8d} | {st['sloc']:8d} | {st['blank']:6d} | {st['comment']:7d}")
    print("-" * 86)
    print(f"{'TOTAL ACROSS ALL DIRECTORIES':38} | {total_files:6d} | {total_lines:8d} | {total_sloc:8d} | {total_blank:6d} | {total_comment:7d}")
    print("=" * 86)

    print("\n" + "=" * 76)
    print(f"{'Language':28} | {'Files':>6} | {'Total':>8} | {'SLOC':>8} | {'Blank':>6} | {'Comment':>7}")
    print("=" * 76)
    for l_name, st in sorted(lang_stats.items()):
        print(f"{l_name:28} | {st['files']:6d} | {st['total']:8d} | {st['sloc']:8d} | {st['blank']:6d} | {st['comment']:7d}")
    print("-" * 76)
    print(f"{'TOTAL ACROSS ALL LANGUAGES':28} | {total_files:6d} | {total_lines:8d} | {total_sloc:8d} | {total_blank:6d} | {total_comment:7d}")
    print("=" * 76)


if __name__ == "__main__":
    count_repository()
