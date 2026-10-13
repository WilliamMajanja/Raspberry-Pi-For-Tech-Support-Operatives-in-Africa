#!/usr/bin/env python3
"""Compatibility entry point for FieldKit's standard-library cover generator."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fieldkit.coffee_snake import main


if __name__ == "__main__":
    raise SystemExit(main())
