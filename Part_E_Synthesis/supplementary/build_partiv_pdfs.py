#!/usr/bin/env python3
"""Build Part IV PDFs into section-prefixed release names."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

def _find_release_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "Part_A_Earth_Systems").is_dir() and (candidate / "Part_E_Synthesis").is_dir():
            return candidate
    raise RuntimeError("Could not locate the CDFD Part IV release root")


RELEASE_ROOT = _find_release_root()
BUILD_ROOT = Path(os.environ.get("CDFD_PARTIV_BUILD_DIR", "/tmp/cdfd_partiv_build"))

PART_LETTERS = {
    "Part_A_Earth_Systems": "A",
    "Part_B_Engineered_Systems": "B",
    "Part_C_Socioeconomic_Systems": "C",
    "Part_D_Domain_Applications": "D",
    "Part_E_Synthesis": "E",
    "Part_F_Cosmic_and_Subatomic_Systems": "F",
    "Part_G_Abstract_and_Cognitive_Systems": "G",
}


def tex_files() -> list[Path]:
    files: list[Path] = []
    for part in PART_LETTERS:
        files.extend((RELEASE_ROOT / part / "papers").glob("*.tex"))
    return sorted(files)


def release_pdf_name(tex_path: Path) -> str:
    relative = tex_path.relative_to(RELEASE_ROOT)
    part = relative.parts[0]
    letter = PART_LETTERS[part]
    pieces = tex_path.stem.split("_")
    number = int(pieces[0])
    rest = "_".join(pieces[1:])
    return f"{letter}{number:02d}_{rest}.pdf"


def release_pdf_path(tex_path: Path) -> Path:
    relative = tex_path.relative_to(RELEASE_ROOT)
    part = relative.parts[0]
    return RELEASE_ROOT / part / "PDFs" / release_pdf_name(tex_path)


def compile_one(tex_path: Path) -> tuple[bool, str]:
    command = [
        "latexmk",
        "-pdf",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-outdir={BUILD_ROOT}",
        str(tex_path),
    ]
    result = subprocess.run(command, cwd=RELEASE_ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        log_tail = "\n".join((result.stdout + result.stderr).splitlines()[-40:])
        return False, f"{tex_path.relative_to(RELEASE_ROOT)}\n{log_tail}"

    built_pdf = BUILD_ROOT / f"{tex_path.stem}.pdf"
    if not built_pdf.exists():
        return False, f"{tex_path.relative_to(RELEASE_ROOT)} did not produce {built_pdf}"

    target = release_pdf_path(tex_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(built_pdf, target)
    return True, str(target.relative_to(RELEASE_ROOT))


def main() -> int:
    BUILD_ROOT.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    written: list[str] = []

    for tex_path in tex_files():
        ok, detail = compile_one(tex_path)
        if ok:
            written.append(detail)
        else:
            failures.append(detail)

    print(f"compiled {len(written)} PDFs into per-Part PDFs folders")
    if failures:
        print(f"failures: {len(failures)}")
        for failure in failures:
            print("\n--- failure ---")
            print(failure)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
