from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]
PYTHON_ENTRYPOINT = ROOT / "scripts" / "pyinstaller_entry.py"

VERSION_FILE = ROOT / "explain_this_repo" / "_version.py"

NODE_NATIVE_ROOT = ROOT / "node_version" / "dist" / "native"
BUILD_ROOT = ROOT / "build" / "pyinstaller"


def normalize_arch(machine: str) -> str:
    machine = machine.lower()
    if machine in {"x86_64", "amd64"}:
        return "x64"
    if machine in {"arm64", "aarch64"}:
        return "arm64"
    raise RuntimeError(f"Unsupported architecture: {machine}")


def platform_key() -> tuple[str, str, str]:
    system = platform.system().lower()
    arch = normalize_arch(platform.machine())

    if system == "darwin":
        return "darwin", arch, "explainthisrepo"
    if system == "linux":
        return "linux", arch, "explainthisrepo"
    if system == "windows":
        return "win", arch, "explainthisrepo.exe"

    raise RuntimeError(f"Unsupported platform: {system}")


def read_project_version() -> str:
    pyproject = ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))

    project = data.get("project")
    if isinstance(project, dict):
        version = project.get("version")
        if isinstance(version, str) and version.strip():
            return version.strip()

    tool = data.get("tool", {})
    if isinstance(tool, dict):
        poetry = tool.get("poetry")
        if isinstance(poetry, dict):
            version = poetry.get("version")
            if isinstance(version, str) and version.strip():
                return version.strip()

    raise RuntimeError("Could not determine project version from pyproject.toml")


def write_version_file(version: str) -> None:
    VERSION_FILE.write_text(f'VERSION = "{version}"\n', encoding="utf-8")


def main() -> None:
    os_name, arch, binary_name = platform_key()
    target_name = f"{os_name}-{arch}"

    version = read_project_version()
    write_version_file(version)

    work_dir = BUILD_ROOT / target_name / "work"
    dist_dir = BUILD_ROOT / target_name / "dist"
    spec_dir = BUILD_ROOT / target_name / "spec"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--console",
        "--name",
        "explainthisrepo",
        "--distpath",
        str(dist_dir),
        "--workpath",
        str(work_dir),
        "--specpath",
        str(spec_dir),
        "--copy-metadata",
        "explainthisrepo",
        "--collect-submodules",
        "explain_this_repo",
        "--collect-submodules",
        "explain_this_repo.providers",
        str(PYTHON_ENTRYPOINT),
    ]

    print("Building PyInstaller binary...")
    print(" ".join(cmd))
    subprocess.run(cmd, cwd=str(ROOT), check=True)

    built_binary = dist_dir / binary_name
    if not built_binary.exists():
        raise RuntimeError(f"Build failed, missing binary: {built_binary}")

    stage_dir = NODE_NATIVE_ROOT / target_name
    stage_dir.mkdir(parents=True, exist_ok=True)

    staged_binary = stage_dir / binary_name
    shutil.copy2(built_binary, staged_binary)

    if os_name != "win":
        staged_binary.chmod(0o755)

    print(f"Staged binary: {staged_binary}")


if __name__ == "__main__":
    main()