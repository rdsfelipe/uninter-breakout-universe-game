"""Build the game executable and copy distributable assets.

PyInstaller embeds the assets into the one-file executable, but this project
also keeps a plain `dist/assets/` copy to make the final build folder easier to
inspect and distribute for coursework review.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT_DIR / "assets"
DIST_DIR = ROOT_DIR / "dist"
DIST_ASSET_DIR = DIST_DIR / "assets"


def run_pyinstaller() -> None:
    """Run PyInstaller with the platform-specific --add-data separator."""
    separator = ";" if os.name == "nt" else ":"
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        "--name",
        "BreakoutUniverse",
        "--add-data",
        f"assets{separator}assets",
        "main.py",
    ]
    subprocess.run(command, cwd=ROOT_DIR, check=True)


def copy_assets() -> None:
    """Copy asset files next to the executable in dist/assets."""
    if not ASSET_DIR.exists():
        raise FileNotFoundError(f"Asset folder not found: {ASSET_DIR}")

    if DIST_ASSET_DIR.exists():
        shutil.rmtree(DIST_ASSET_DIR)

    shutil.copytree(ASSET_DIR, DIST_ASSET_DIR)


def main() -> None:
    run_pyinstaller()
    copy_assets()
    print(f"Build complete: {DIST_DIR}")
    print(f"Assets copied to: {DIST_ASSET_DIR}")


if __name__ == "__main__":
    main()
