#!/usr/bin/env python3
"""Retired compatibility entrypoint for the pre-consolidation manuscript upgrader."""

from __future__ import annotations

import sys


MESSAGE = """This pre-consolidation upgrader is retired for Part IV revision 1.1.0.
It carried profiles for the former 58-paper release and can recreate the shared
template text intentionally moved to PART_IV_METHODS_AND_CLAIM_BOUNDARY.md.
Edit a named active manuscript deliberately, then run the active audit and
build workflows. Do not use this script to regenerate Part IV.
"""


def main() -> int:
    print(MESSAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
