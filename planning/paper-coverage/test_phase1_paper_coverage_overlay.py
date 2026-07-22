#!/usr/bin/env python3
"""Scoped tests for the human-reviewed Phase-1 coverage overlay."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OVERLAY = HERE / "phase1-paper-coverage-overlay-2026-07-22.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_overlay_is_independently_verified() -> None:
    verifier = load(HERE / "verify_phase1_paper_coverage_overlay.py", "coverage_verifier")
    verifier.verify(json.loads(OVERLAY.read_text()))


def test_exactly_eight_results_are_human_classified() -> None:
    payload = json.loads(OVERLAY.read_text())
    materiality = [node for node in payload["nodes"] if node["kind"] == "materiality"]
    assert len(materiality) == 8
    assert {node["body"]["by"] for node in materiality} == {"Asger Alstrup Palm"}


def test_overview_mentions_do_not_masquerade_as_technical_coverage() -> None:
    payload = json.loads(OVERLAY.read_text())
    overview_ids = {
        "paper:00-ghosts-geometry-reality",
        "paper:98-physicist-executive-summary",
        "paper:99-how-to-build-a-universe",
    }
    for node in payload["nodes"]:
        if node["kind"] == "result_paper_edge" and node["body"]["to"] in overview_ids:
            assert node["body"]["edge_kind"] == "OVERVIEW_MENTION"
