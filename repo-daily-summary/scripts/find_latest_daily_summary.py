#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def find_latest_summary(directory: Path) -> Path | None:
    summaries = sorted(
        directory.glob("daily_summary_*.md"),
        key=lambda path: (path.name, path.stat().st_mtime),
    )
    return summaries[-1] if summaries else None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print the latest daily_summary_*.md in a directory."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Target directory to scan. Defaults to the current directory.",
    )
    args = parser.parse_args()

    directory = Path(args.directory).expanduser().resolve()
    if not directory.exists():
        raise SystemExit(f"Directory does not exist: {directory}")
    if not directory.is_dir():
        raise SystemExit(f"Not a directory: {directory}")

    latest = find_latest_summary(directory)
    if latest is not None:
        print(latest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
