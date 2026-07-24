#!/usr/bin/env python3
"""Verify panels 270--277 without rerunning their transport."""
from .runner import CONFIG
from ..continuation import verify


def main() -> None:
    verify(CONFIG)


if __name__ == "__main__":
    main()
