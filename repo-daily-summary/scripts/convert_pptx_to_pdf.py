#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


def find_converter(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if not path.is_file():
            raise SystemExit(f"Converter does not exist: {path}")
        return path

    for command in ("libreoffice", "soffice"):
        resolved = shutil.which(command)
        if resolved:
            return Path(resolved)
    raise SystemExit(
        "LibreOffice is required for PPTX-to-PDF conversion. "
        "Install libreoffice/soffice or pass --converter."
    )


def pptx_slide_count(path: Path) -> int:
    pattern = re.compile(r"^ppt/slides/slide\d+\.xml$")
    with zipfile.ZipFile(path) as archive:
        count = sum(bool(pattern.match(name)) for name in archive.namelist())
    if count == 0:
        raise SystemExit(f"No slides found in PPTX: {path}")
    return count


def pdf_page_count(path: Path) -> int | None:
    pdfinfo = shutil.which("pdfinfo")
    if not pdfinfo:
        return None
    result = subprocess.run(
        [pdfinfo, str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    match = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, re.MULTILINE)
    if not match:
        raise SystemExit(f"Could not read PDF page count: {path}")
    return int(match.group(1))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert a PPTX to PDF with LibreOffice and validate page count."
    )
    parser.add_argument("pptx", help="Input PowerPoint file.")
    parser.add_argument(
        "--output",
        help="Output PDF path. Defaults to the PPTX path with a .pdf suffix.",
    )
    parser.add_argument(
        "--converter",
        help="Explicit path to libreoffice or soffice.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing output PDF.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print the planned conversion without running it.",
    )
    args = parser.parse_args()

    pptx = Path(args.pptx).expanduser().resolve()
    if not pptx.is_file():
        raise SystemExit(f"PPTX does not exist: {pptx}")
    if pptx.suffix.lower() != ".pptx":
        raise SystemExit(f"Expected a .pptx input: {pptx}")

    output = (
        Path(args.output).expanduser().resolve()
        if args.output
        else pptx.with_suffix(".pdf")
    )
    if output.suffix.lower() != ".pdf":
        raise SystemExit(f"Expected a .pdf output: {output}")
    if output.exists() and not args.force:
        raise SystemExit(f"Output already exists; pass --force to replace it: {output}")

    converter = find_converter(args.converter)
    expected_pages = pptx_slide_count(pptx)

    if args.dry_run:
        print(f"converter={converter}")
        print(f"input={pptx}")
        print(f"output={output}")
        print(f"expected_pages={expected_pages}")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="repo-summary-pdf-") as temp:
        temp_root = Path(temp)
        converted_dir = temp_root / "converted"
        profile_dir = temp_root / "libreoffice-profile"
        converted_dir.mkdir()
        profile_dir.mkdir()
        command = [
            str(converter),
            "--headless",
            f"-env:UserInstallation={profile_dir.as_uri()}",
            "--convert-to",
            "pdf",
            "--outdir",
            str(converted_dir),
            str(pptx),
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise SystemExit(
                f"LibreOffice conversion failed ({result.returncode}):\n"
                f"{result.stdout}{result.stderr}"
            )

        converted = converted_dir / f"{pptx.stem}.pdf"
        if not converted.is_file() or converted.stat().st_size == 0:
            raise SystemExit(
                "LibreOffice reported success but did not produce a non-empty PDF:\n"
                f"{result.stdout}{result.stderr}"
            )
        if output.exists():
            output.unlink()
        shutil.move(str(converted), output)

    actual_pages = pdf_page_count(output)
    if actual_pages is not None and actual_pages != expected_pages:
        output.unlink(missing_ok=True)
        raise SystemExit(
            f"PDF page count mismatch: expected {expected_pages}, got {actual_pages}"
        )

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
