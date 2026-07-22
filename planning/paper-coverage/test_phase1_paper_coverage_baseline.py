#!/usr/bin/env python3
"""Scoped tests for the Phase-1 publication-coverage baseline."""

from __future__ import annotations

import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_committed_baseline_is_consistent() -> None:
    verifier = load(HERE / "verify_phase1_paper_coverage_baseline.py", "baseline_verifier")
    verifier.verify(
        HERE / "phase1-paper-coverage-baseline-2026-07-22.json",
        HERE / "phase1-paper-coverage-report-2026-07-22.json",
        HERE / "phase1-paper-coverage-overlay-2026-07-22.json",
        None,
    )
