#!/usr/bin/env python3
"""Regenerate all public Part IV runtime discovery artifacts."""
from __future__ import annotations

from partiv_runtime import run_release_diagnostics


def main() -> int:
    run_release_diagnostics()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
