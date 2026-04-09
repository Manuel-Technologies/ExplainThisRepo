from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LocalReadResult:
    tree: list[str]
    tree_text: str
    key_files: dict[str, str]
    files_text: str


_KEY_FILENAMES = {
    "readme.md",
    "readme.txt",
    "readme.rst",
    "readme",
    "package.json",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "composer.json",
    "gemfile",
    "makefile",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".env.example",
    "tsconfig.json",
    "angular.json",
    "next.config.js",
    "vite.config.js",
    "vite.config.ts",
    "webpack.config.js",
}

_SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".env",
    "dist",
    "build",
    ".idea",
    ".vscode",
    ".mypy_cache",
    ".pytest_cache",
    "coverage",
    ".coverage",
    "htmlcov",
}

_MAX_FILE_BYTES = 32_000
_MAX_KEY_FILES = 12


def _is_key_filename(filename: str) -> bool:
    return filename.lower() in _KEY_FILENAMES


def _read_text_file(path: Path, max_bytes: int) -> str:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return handle.read(max_bytes)


def _build_files_text(key_files: dict[str, str]) -> str:
    if not key_files:
        return ""
    return "\n\n".join(
        f"### {rel_path}\n{content}" for rel_path, content in key_files.items()
    )


def read_local_repo_signal_files(path: str) -> LocalReadResult:
    root = Path(path).expanduser()

    if not root.exists():
        raise FileNotFoundError(f"No such directory: {path}")

    if not root.is_dir():
        raise ValueError(f"Not a directory: {path}")

    root = root.resolve()

    tree_lines: list[str] = []
    key_files: dict[str, str] = {}

    for dirpath, dirnames, filenames in os.walk(str(root)):
        dirnames[:] = sorted(d for d in dirnames if d not in _SKIP_DIRS)

        current_dir = Path(dirpath).relative_to(root)
        prefix = "" if str(current_dir) == "." else f"{current_dir.as_posix()}/"

        for filename in sorted(filenames):
            rel_path = f"{prefix}{filename}"
            tree_lines.append(rel_path)

            if not _is_key_filename(filename):
                continue

            if len(key_files) >= _MAX_KEY_FILES:
                continue

            full_path = Path(dirpath) / filename

            try:
                key_files[rel_path] = _read_text_file(full_path, _MAX_FILE_BYTES)
            except OSError:
                continue

    tree_text = "\n".join(tree_lines)
    files_text = _build_files_text(key_files)

    return LocalReadResult(
        tree=tree_lines,
        tree_text=tree_text,
        key_files=key_files,
        files_text=files_text,
    )
