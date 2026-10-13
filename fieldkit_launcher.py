#!/usr/bin/env python3
"""PyInstaller entry point for the standalone FieldKit application."""

from fieldkit.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
