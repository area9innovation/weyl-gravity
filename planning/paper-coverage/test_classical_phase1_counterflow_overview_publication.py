#!/usr/bin/env python3
"""Scoped tests for the counterflow overview publication update."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "planning/paper-coverage/generate_classical_phase1_counterflow_overview_publication.py"
VERIFY = ROOT / "planning/paper-coverage/verify_classical_phase1_counterflow_overview_publication.py"
RECORD = ROOT / "planning/paper-coverage/classical-phase1-counterflow-overview-publication-2026-07-21.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_generated_record_is_current() -> None:
    generator = load(GEN, "phase1_overview_generator")
    assert generator.build() == json.loads(RECORD.read_text())


def test_independent_verifier() -> None:
    verifier = load(VERIFY, "phase1_overview_verifier")
    verifier.verify(json.loads(RECORD.read_text()))


def test_terminal_scope_is_fail_closed() -> None:
    payload = json.loads(RECORD.read_text())
    claims = payload["claims_propagated"]
    assert claims["selected_fixture_causal_parent"] is True
    assert claims["causal_parent_implies_physical_health"] is False
    assert claims["phase2_candidate_selected"] is False
    assert claims["higher_isotype_retuning_spectrum_complete"] is False
    assert claims["universal_changed_architecture_no_go"] is False
