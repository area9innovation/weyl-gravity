#!/usr/bin/env python3
"""Verify panels 821--828 without rerunning their transport."""
from .runner import CONFIG
from ..continuation import verify


def main() -> None:
    verify(CONFIG)


if __name__ == "__main__":
    main()

